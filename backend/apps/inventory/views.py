from rest_framework import permissions, viewsets
from .models import Item
from .serializers import ItemSerializer


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ItemSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Item.objects.filter(source_task__created_by=self.request.user).order_by("-obtained_at")



