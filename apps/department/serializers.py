from django.contrib.auth.models import Permission
from django.conf import settings
from rest_framework import serializers
from .models import Department
from core.serializers.fields import PrimaryKey_To_ObjectField
from apps.user.models import User


class DepartmentMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "designation")


class DepartmentSerializer(serializers.ModelSerializer):
    heads = PrimaryKey_To_ObjectField(
        queryset=User.objects.all(),
        object_serializer=DepartmentMemberSerializer,
        many=True,
        required=False,
    )
    permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all()
    )
    # members is a list of user objects that belong to this dept.
    members = DepartmentMemberSerializer(read_only=True, many=True)

    class Meta:
        model = Department
        fields = ("id", "name", "description", "members", "heads", "permissions")

    def to_representation(self, instance):
        """
        We override the default members repr. to use actual User objects
        instead of UserTenantPermissions
        """
        members = [user.profile for user in instance.user_set.all()]
        repr = super().to_representation(instance)
        repr["members"] = DepartmentMemberSerializer(members, many=True).data
        repr["permissions"] = self._get_perms_data(instance)
        return repr

    def validate_heads(self, value):
        if len(value) > Department.MAX_NUMBER_OF_HEADS:
            raise serializers.ValidationError(
                f"Max of {Department.MAX_NUMBER_OF_HEADS} users can head a department."
            )
        return value

    def create(self, validated_data):
        # heads should not be added on create
        validated_data.pop("heads", None)
        instance = super().create(validated_data)
        return instance

    def _get_perms_data(self, instance):
        """
        Return all dept. permissions but, categorised by predefined
        categories in `settings.PERMISSION_CATEGORIES`.

        e.g:
        "sales": {
            "invoice": [
                {
                    "id": 1,
                    "name": "Can view invoice",
                    "codename": "view_invoice"
                }
            ]
        }
        """

        perms_categories = settings.PERMISSION_CATEGORIES
        perms_by_categories = {}
        for perm in instance.permissions.select_related("content_type"):
            perm_model = perm.content_type.name
            perm_dict = {"id": perm.id, "name": perm.name, "codename": perm.codename}
            for category, models in perms_categories.items():
                if perm_model not in models:
                    continue
                if category not in perms_by_categories:
                    perms_by_categories[category] = {}
                if perm_model in perms_by_categories[category]:
                    perms_by_categories[category][perm_model].append(perm_dict)
                else:
                    perms_by_categories[category][perm_model] = [perm_dict]
        return perms_by_categories


class UpdateDepartmentMembersSerializer(serializers.Serializer):
    users = serializers.ListField(child=serializers.IntegerField(), write_only=True)

    def update_members(self, instance, validated_data):
        action = self.context["action"]
        user_ids = validated_data["users"]
        users = User.objects.filter(id__in=user_ids)
        if users:
            if action == "add":
                response = instance.add_members(users)
            elif action == "remove":
                response = instance.remove_members(users)
            else:
                raise ValueError(f"Invalid action type'{action}'")
            return response
        else:
            raise serializers.ValidationError("No valid user sent.")


class DepartmentPermissionSerializer(serializers.ModelSerializer):
    module = serializers.CharField(source="content_type.app_label")
    model = serializers.CharField(source="content_type.model")

    class Meta:
        model = Permission
        fields = ("id", "name", "codename", "module", "model")


class DepartmentAsRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name")
