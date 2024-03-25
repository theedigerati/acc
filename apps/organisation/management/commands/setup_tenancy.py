from django.conf import settings
from django.db import transaction
from django.core.management.base import BaseCommand
from apps.organisation.models import OrgAddress, Organisation, Tenant
from apps.user.models import User
from tenant_users.tenants.utils import create_public_tenant
from tenant_users.tenants.tasks import provision_tenant


class Command(BaseCommand):
    help = "Create public tenant and default Organisation."

    def handle(self, *args, **options):
        domain = settings.TENANT_USERS_DOMAIN
        public_owner = settings.BASE_TENANT_OWNER_EMAIL

        self.create_public_tenant(domain, public_owner)
        self.setup_default_organisation(public_owner)

        self.stdout.write("Tenancy setup done!")

    @transaction.atomic
    def create_public_tenant(self, domain, public_owner):
        if not Tenant.objects.filter(schema_name="public").exists():
            self.stdout.write("creating public tenant...")
            create_public_tenant(domain, public_owner, is_staff=True, is_superuser=True)
            self.stdout.write(
                f"Public tenant created with {domain} as domain and {public_owner} as owner"
            )
        else:
            self.stdout.write("Public tenant already exists!")

    @transaction.atomic
    def setup_default_organisation(self, public_owner):
        if Organisation.objects.first() is None:
            self.stdout.write("creating default organisation...")
            org_name = "default"
            provision_tenant(
                tenant_name=org_name, tenant_slug=org_name, user_email=public_owner
            )
            tenant = Tenant.objects.get(slug=org_name)
            address = OrgAddress.objects.create(
                line1="25 Rahman Str.",
                line2="Off B Road",
                city="Gwarimpa",
                state="Abuja",
                postcode="100213",
                country="Nigeria",
            )
            org = Organisation.objects.create(
                name="Default Organisation",
                address=address,
                tenant=tenant,
            )
            self.stdout.write(f"{org.name} has been created successfully")

            self.stdout.write("updating public owner details...")
            owner = User.objects.get(email=public_owner)
            owner.first_name = "Meta"
            owner.last_name = "User"
            owner.role = "meta"
            owner.set_password("password")
            owner.save()
            self.stdout.write("Tenancy setup done!")
        else:
            self.stdout.write("Default organisation already exists!")

    # for org in Organisation.objects.select_related("tenant"):
    #         self.generate_accounts(org.tenant.schema_name)
    #         self.add_all_meta_users(org)

    # def generate_accounts(self, schema_name):
    #     self.stdout.write("generating default accounts...")
    #     accounting_factory = AccountingFactory(schema_name)
    #     accounting_factory.generate_default_accounts()
    #     self.stdout.write("Default accounts generated")

    # def add_all_meta_users(self, org):
    #     self.stdout.write(f"Adding meta users to {org.name}...")
    #     meta_users = User.objects.filter(role="meta")
    #     org.add_users(meta_users)
    #     self.stdout.write("Done!")
