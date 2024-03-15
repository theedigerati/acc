from django.db import models
from django.contrib.auth.models import Group, Permission
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist


class Department(Group):
    """
    A department is a (Group) of users in an organisation.
    Departments can be given specific permissions just like Group.
    Departments can have heads(with specific permissions) unlike Group.
    """

    description = models.CharField(max_length=200)
    heads = models.ManyToManyField(
        "user.User",
        blank=True,
        help_text=_("Department heads"),
        related_name="heading_departments",
    )

    MAX_NUMBER_OF_HEADS = 2

    class Meta:
        verbose_name = _("department")
        verbose_name_plural = _("departments")
        permissions = [
            ("custom_change_department_as_head", "Can change department as head")
        ]

    def save(self, *args, **kwargs):
        if self._state.adding is False:
            perm = Permission.objects.get(codename="custom_change_department_as_head")
            for head in self.heads.all():
                self.add_members([head])
                head.tenant_perms.user_permissions.add(perm)
        return super().save(*args, **kwargs)

    def add_members(self, users):
        res = {"added": 0, "nonexistent": 0}
        for user in users:
            try:
                self.user_set.add(user.tenant_perms)
                res["added"] += 1
            except ObjectDoesNotExist:
                res["nonexistent"] += 1
        return res

    def remove_members(self, members):
        res = {"removed": 0, "nonexistent": 0}
        for member in members:
            try:
                self.user_set.remove(member.tenant_perms)
                res["removed"] += 1
            except ObjectDoesNotExist:
                res["nonexistent"] += 1
        return res

    def add_permissions(self, *perms):
        permissions = Permission.objects.filter(codename__in=list(perms))
        self.permissions.add(*permissions)
