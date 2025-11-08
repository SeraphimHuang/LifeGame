from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttributeMappingViewSet, DropConfigViewSet

router = DefaultRouter()
router.register(r"mapping", AttributeMappingViewSet, basename="attribute-mapping")
router.register(r"drop-config", DropConfigViewSet, basename="drop-config")

urlpatterns = [
    path("", include(router.urls)),
]



