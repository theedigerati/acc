from django.db import models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from tenant_users.tenants.models import TenantBase, ExistsError, DeleteError
from django_tenants.models import DomainMixin
from tenant_users.tenants.tasks import provision_tenant
from apps.user.models import User
from core.abstract_models import AbstractAddress
from apps.accounting.factory import AccountingFactory


class Tenant(TenantBase):
    name = models.CharField(max_length=100)


class OrgAddress(AbstractAddress):
    class Meta:
        default_permissions = []


class Organisation(models.Model):
    name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, default="HQ")
    description = models.TextField(max_length=255, blank=True)
    address = models.ForeignKey(
        "organisation.OrgAddress",
        related_name="organisations",
        on_delete=models.SET_NULL,
        null=True,
    )
    phone = models.CharField(max_length=15, blank=True)
    tenant = models.OneToOneField(
        "organisation.Tenant", related_name="organisation", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ("name", "branch")
        permissions = [
            ("custom_update_users", "Can add/remove users"),
            ("custom_view_all_organisations", "Can view all organisations"),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                self.tenant
            except ObjectDoesNotExist:
                self._create_tenant()
            finally:
                self._add_all_meta_users()
                accounting_factory = AccountingFactory(self.tenant.schema_name)
                accounting_factory.generate_default_accounts()
        else:
            self._update_tenant()

        super().save(*args, **kwargs)

    @property
    def full_name(self) -> str:
        return f"{self.name}, {self.branch}."

    @property
    def tenant_slug(self) -> str:
        return self.tenant.slug

    @property
    def users(self):
        return self.tenant.user_set.count()

    def add_users(self, users: list = []):
        res = {"added": 0, "exist": 0}
        for user in users:
            try:
                self.tenant.add_user(user)
                user.assign_default_permissions()
                res["added"] += 1
            except ExistsError:
                res["exist"] += 1
        return res

    def remove_users(self, users: list = []):
        res = {"removed": 0, "nonexistent": 0}
        for user in users:
            try:
                self.tenant.remove_user(user)
                res["removed"] += 1
            except ObjectDoesNotExist:
                res["nonexistent"] += 1
            except DeleteError:
                pass
        return res

    def get_tenant_slug(self):
        org_name = self.name.replace(" ", "-")
        org_branch = self.branch.lower()
        return f"{org_name}-{org_branch}"

    def _create_tenant(self):
        tenant_slug = self.get_tenant_slug()
        # TODO: run this on a celery task
        provision_tenant(
            tenant_name=self.name,
            tenant_slug=tenant_slug,
            user_email=settings.BASE_TENANT_OWNER_EMAIL,
        )
        self.tenant = Tenant.objects.get(slug=tenant_slug)

    def _update_tenant(self):
        tenant_slug = self.get_tenant_slug()
        Tenant.objects.filter(id=self.tenant.id).update(
            name=self.name, slug=tenant_slug
        )

    def _add_all_meta_users(self):
        meta_users = User.objects.filter(role=User.META)
        self.add_users(list(meta_users))


class Domain(DomainMixin):
    pass
