from __future__ import annotations

from django.db.models import Prefetch
from rest_framework import permissions, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse
from rest_framework.response import Response

from menu.models import FoodItem, MenuSection, MysteryBox
from .models import Business
from .serializers import (
    HomeDiscoverySerializer,
    RestaurantListSerializer,
    RestaurantSerializer,
)


class RestaurantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only entry point for restaurant catalogue data including menu sections and extras.
    """

    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        if self.action == "list":
            return (
                Business.objects.all()
                .select_related("category")
                .only(
                    "id",
                    "name",
                    "tagline",
                    "hero_image_url",
                    "image_url",
                    "average_rating",
                    "review_count",
                    "delivery_time_minutes_min",
                    "delivery_time_minutes_max",
                    "delivery_available",
                    "category__name",
                )
            )

        menu_section_qs = (
            MenuSection.objects.order_by("position", "id")
            .prefetch_related("food_items__extra_groups__group__extras")
            .prefetch_related("food_items__section")
        )
        mystery_box_qs = MysteryBox.objects.filter(is_active=True).prefetch_related(
            "extra_group_links__group__extras"
        )

        return (
            Business.objects.all()
            .select_related("category")
            .prefetch_related(
                Prefetch("menu_sections", queryset=menu_section_qs),
                Prefetch("mystery_boxes", queryset=mystery_box_qs),
            )
        )

    def get_serializer_class(self):
        if self.action == "list":
            return RestaurantListSerializer
        return RestaurantSerializer


class HomeDiscoveryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        businesses = Business.objects.select_related("category")
        featured = businesses.order_by("-average_rating", "-review_count")[:5]
        near_you = businesses.order_by("delivery_time_minutes_min", "name")[:6]
        most_ordered_items = (
            FoodItem.objects.select_related("business")
            .filter(is_available=True)
            .order_by("-is_discounted", "-discount_percentage", "-created_at")[:6]
        )
        featured_products = (
            FoodItem.objects.select_related("business")
            .filter(is_available=True)
            .order_by("-discount_percentage", "-is_discounted", "name")[:8]
        )

        serializer = HomeDiscoverySerializer(
            {
                "featuredRestaurants": featured,
                "mostOrderedThisWeek": most_ordered_items,
                "nearYouRestaurants": near_you,
                "featuredProducts": featured_products,
            }
        )
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def api_root(request, format=None):
    return Response(
        {
            "home": reverse("home-discovery", request=request, format=format),
            "restaurants": reverse("restaurant-list", request=request, format=format),
            "products": reverse("product-list", request=request, format=format),
            "offers": reverse("offer-list", request=request, format=format),
        }
    )
