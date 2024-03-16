from django.contrib import admin
from django.urls import path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from rest_framework.routers import SimpleRouter

from apps.organisation.views import OrganisationViewSet
from apps.user.views import UserViewSet
from apps.department.views import DepartmentViewSet
from apps.user.views import PermissionViewSet
from apps.inventory.item.views import ItemViewSet
from apps.inventory.item.views import ServiceViewSet
from apps.tax.views import TaxViewSet
from apps.accounting.views import AccountViewSet


@api_view()
@authentication_classes([])
@permission_classes([])
def main(request):
    return Response({"message": "Accounting API!"})


urlpatterns = [
    path("", main, name="home"),
    path("admin/", admin.site.urls),
    # auth
    path("auth/login/", TokenObtainPairView.as_view(), name="jwt-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
]

router = SimpleRouter()
router.register(r"organisations", OrganisationViewSet)
router.register(r"users", UserViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"permissions", PermissionViewSet)
router.register(r"items", ItemViewSet)
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"taxes", TaxViewSet, basename="tax")
router.register(r"accounts", AccountViewSet)

urlpatterns += router.urls
urlpatterns += staticfiles_urlpatterns()

handler500 = "rest_framework.exceptions.server_error"
