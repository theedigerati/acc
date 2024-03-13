from django.contrib import admin
from django.urls import path
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
