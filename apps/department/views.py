from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions

from apps.user.serializers import PermissionSerializer
from .models import Department
from .serializers import (
    DepartmentMemberSerializer,
    DepartmentSerializer,
    UpdateDepartmentMembersSerializer,
)
from core.permissions import BelongsToOrganisation, BaseModelPermissions


class UpdateDepartmentAsHead(DjangoModelPermissions):
    """
    Ensures that rquest user has the permission of a department head,
    belongs to the department and is one the heads.
    """

    perms_map = {
        "GET": ["%(app_label)s.custom_change_department_as_head"],
        "OPTIONS": ["%(app_label)s.custom_change_department_as_head"],
        "HEAD": ["%(app_label)s.custom_change_department_as_head"],
        "POST": ["%(app_label)s.custom_change_department_as_head"],
        "PUT": ["%(app_label)s.custom_change_department_as_head"],
        "PATCH": ["%(app_label)s.custom_change_department_as_head"],
    }

    def has_object_permission(self, request, view, obj):
        request_user_is_member = obj.user_set.filter(
            profile__id=request.user.id
        ).exists()
        request_user_is_head = obj.heads.filter(id=request.user.id).exists()
        return request_user_is_member and request_user_is_head


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def get_permissions(self):
        if self.action in [
            "update",
            "partial_update",
            "add_members",
            "remove_members",
            "all_permissions",
            "non_members",
        ]:
            self.permission_classes = [
                BelongsToOrganisation,
                UpdateDepartmentAsHead | BaseModelPermissions,
            ]
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [BelongsToOrganisation, DjangoModelPermissions]
        return super().get_permissions()

    def check_object_permissions(self, request, obj):
        """
        Only mgt. users can update dept. permissions.
        i.e only users with the 'change_department' permission.
        """
        is_update_request = self.action == "update" or self.action == "partial_update"
        if is_update_request and "permissions" in request.data:
            # check that it is an update
            dept_permissions_data = request.data.get("permissions", [])
            current_dept_permissions = obj.permissions.values_list("id", flat=True)
            is_updating_permissions = set(dept_permissions_data) != set(
                current_dept_permissions
            )

            if (
                is_updating_permissions
                and request.user.has_perm("department.change_department") is False
            ):
                raise PermissionDenied(
                    "You're not permitted to update this department's permissions."
                )

        return super().check_object_permissions(request, obj)

    @action(methods=["get"], detail=True)
    def all_permissions(self, request, pk=None):
        instance = self.get_object()
        permissions = instance.permissions.all()
        ser = PermissionSerializer(permissions, many=True)
        return Response(ser.data)

    @action(methods=["post"], detail=True)
    def add_members(self, request, pk=None):
        response = self._update_members(request, "add")
        return Response(response)

    @action(methods=["post"], detail=True)
    def remove_members(self, request, pk=None):
        response = self._update_members(request, "remove")
        return Response(response)

    @action(methods=["get"], detail=True)
    def non_members(self, request, pk=None):
        instance = self.get_object()
        members = instance.user_set.values_list("profile__id", flat=True)
        non_members = request.tenant.user_set.exclude(id__in=members)
        serializer = DepartmentMemberSerializer(non_members, many=True)
        return Response(serializer.data)

    def _update_members(self, request, action_type):
        instance = self.get_object()
        ser = UpdateDepartmentMembersSerializer(
            instance, data=request.data, context={"action": action_type}
        )
        if ser.is_valid(raise_exception=True):
            response = ser.update_members(instance, ser.validated_data)
            return response


# TODO: add view action to deactivate department.
