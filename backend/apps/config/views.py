from rest_framework import permissions, viewsets, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import AttributeMapping, DropConfig
from .serializers import AttributeMappingSerializer, DropConfigSerializer


class AttributeMappingViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AttributeMapping.objects.all().order_by("id")
    serializer_class = AttributeMappingSerializer


class DropConfigViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DropConfig.objects.all()
    serializer_class = DropConfigSerializer



