from rest_framework import permissions, viewsets

from .models import FoodItem
from .serializers import FoodItemDetailSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for individual menu items with full modifier information.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = FoodItemDetailSerializer
    queryset = (
        FoodItem.objects.select_related("business")
        .prefetch_related("extra_groups__group__extras")
        .filter(is_available=True)
    )
