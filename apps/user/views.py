from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from django_tenants.utils import schema_context
from core.permissions import BelongsToOrganisation
from .models import User
from .serializers import (
    UserSerializer,
    UserCreateUnsafeSerializer,
    UserLazyUpdateSerializer,
    Permission,
    PermissionSerializer,
)


class CustomModelPermissions(DjangoModelPermissions):
    """
    Enforce role hierarchy access.
    """

    def has_permission(self, request, view):
        has_perms = super().has_permission(request, view)
        if view.action == "create":
            return has_perms and view.can_assign_role(request, request.data.get("role"))
        return has_perms

    def has_object_permission(self, request, view, obj):
        if view.action == "permissions" and obj == request.user:
            return True

        can_retrieve_user = view.can_retrieve_user(request, obj)
        if view.action == "retrieve":
            return can_retrieve_user

        can_assign_role = view.can_assign_role(request, request.data.get("role"))
        can_update_user = view.can_update_user(request, obj)
        can_update = can_retrieve_user and can_update_user and can_assign_role

        if view.action == "permissions":
            return request.user.has_perm("user.change_user") and can_update

        if view.action in ["update", "partial_update", "permissions"]:
            return can_update

        return True


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [BelongsToOrganisation, CustomModelPermissions]

    def get_queryset(self):
        """
        Return users in the request tenant.
        """
        queryset = self.queryset
        tenant = self.request.tenant
        user_ids = tenant.user_set.values_list("id", flat=True)
        return queryset.filter(id__in=user_ids)

    def get_permissions(self):
        if self.action == "me":
            self.permission_classes = [IsAuthenticated]
        if self.action == "my_permissions":
            self.permission_classes = [BelongsToOrganisation]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "me" and (
            self.request.method == "PUT" or self.request.method == "PATCH"
        ):
            return UserLazyUpdateSerializer
        return self.serializer_class

    @schema_context("public")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.delete(force_drop=True)

    @action(["get", "put", "patch"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)
        elif request.method == "PUT":
            return self.update(request, *args, **kwargs)
        elif request.method == "PATCH":
            return self.partial_update(request, *args, **kwargs)

    @action(["get"], detail=False)
    def my_permissions(self, request, *args, **kwargs):
        perms = request.user.get_all_permissions()
        return Response([perm.split(".")[1] for perm in perms])

    @action(["get"], detail=True)
    def permissions(self, request, *args, **kwargs):
        instance = self.get_object()
        serialized_perms = self.get_serialized_permissions(instance)
        return Response(serialized_perms)

    @action(methods=["post"], detail=False)
    def unsafe_create(self, request, *args, **kwargs):
        ser = UserCreateUnsafeSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        with schema_context("public"):
            user = ser.save()
        # add user to the request tenant and asssign permissions
        request.tenant.add_user(user)
        user.assign_default_permissions()
        return Response(ser.data, status=status.HTTP_201_CREATED)

    def get_instance(self):
        return self.request.user

    def get_serialized_permissions(self, user):
        perms = user.get_all_permissions()
        permissions = Permission.objects.filter(
            codename__in=[perm.split(".")[1] for perm in perms]
        )
        ser = PermissionSerializer(permissions, many=True)
        return ser.data

    def can_retrieve_user(self, request, user):
        """
        Check if request user and `user` both belong
        to the request tenant (for public tenant access).
        """
        tenants_for_user = user.tenants.exclude(schema_name="public")
        tenants_for_request_user = request.user.tenants.exclude(schema_name="public")
        return bool(tenants_for_user.intersection(tenants_for_request_user))

    def can_assign_role(self, request, role):
        """
        Check if request user has hierarchy access to assign `role` to a user.
        """
        if role is None:
            return True

        if (
            (request.user.is_employee and role != User.EMPLOYEE)
            or (request.user.is_admin and role == User.META)
            or (request.user.is_manager and role in [User.ADMIN, User.META])
        ):
            return False

        return True

    def can_update_user(self, request, user):
        """
        Check if request user has hierarchy access to update `user`.
        """
        if (
            (request.user.is_employee and user.is_manager_or_more)
            or (request.user.is_admin and user.is_meta)
            or (request.user.is_manager and user.is_admin_or_more)
        ):
            return False

        return True

    # TODO: 6 Tasks
    #
    # 1. Implement user activation.
    # 2. Implement user resend activation.
    # 3. Implement user reset password.
    # 4. Implemrnt user reset password confirm.
    # 5. Implement admin reset password.
    # 6. Implement deactivate user.
