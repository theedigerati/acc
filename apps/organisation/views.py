from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import DjangoModelPermissions
from core.permissions import BelongsToOrganisation
from .models import Organisation
from .serializers import (
    OrganisationSerializer,
    OrganisationUsersUpdateSerializer,
)


class AddRemoveUsers(DjangoModelPermissions):
    perms_map = {"POST": ["%(app_label)s.custom_update_users"]}


class ViewAllOrganisations(DjangoModelPermissions):
    perms_map = {"GET": ["%(app_label)s.custom_view_all_organisations"]}


class OrganisationViewSet(ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

    def get_permissions(self):
        if self.action == "add_users" or self.action == "remove_users":
            self.permission_classes = [BelongsToOrganisation, AddRemoveUsers]
        if self.action == "list":
            self.permission_classes = [BelongsToOrganisation, ViewAllOrganisations]
        return super().get_permissions()

    @action(methods=["post"], detail=False)
    def add_users(self, request):
        response = self._update_users(request, "add")
        return Response(response)

    @action(methods=["post"], detail=False)
    def remove_users(self, request):
        response = self._update_users(request, "remove")
        return Response(response)

    def _update_users(self, request, action_type):
        instance = request.tenant.organisation
        ser = OrganisationUsersUpdateSerializer(
            instance, data=request.data, context={"action": action_type}
        )
        if ser.is_valid(raise_exception=True):
            response = ser.update_users(instance, ser.validated_data)
            return response

    # TODO: implement disable Org.
