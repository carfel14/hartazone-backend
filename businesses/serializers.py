from __future__ import annotations

from typing import Any

from rest_framework import serializers

from menu.serializers import MenuSectionSerializer, MysteryBoxSerializer, ModifierSerializer
from menu.models import FoodItem
from .models import Business, BusinessCategory

CARD_BACKGROUNDS = [
    "#EEF2FF",
    "#FFE8D9",
    "#E8F9F1",
    "#FFF1F8",
    "#E6F0FF",
    "#FDF7E3",
]


def background_for(value: str | int) -> str:
    try:
        index = abs(hash(value)) % len(CARD_BACKGROUNDS)
    except Exception:
        index = 0
    return CARD_BACKGROUNDS[index]


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ("id", "name")


class RestaurantListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    heroImage = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    cuisine = serializers.SerializerMethodField()
    deliveryEta = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "tagline",
            "heroImage",
            "rating",
            "cuisine",
            "deliveryEta",
        )

    def get_heroImage(self, obj: Business) -> str | None:
        return obj.hero_image_url or obj.image_url or ""

    def get_rating(self, obj: Business) -> str | None:
        if obj.average_rating is None:
            return ""
        return f"{obj.average_rating:.1f}"

    def get_cuisine(self, obj: Business) -> str | None:
        return obj.category.name if obj.category else ""

    def get_deliveryEta(self, obj: Business) -> str | None:
        return obj.formatted_delivery_eta() or ""


class RestaurantSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    heroImage = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    cuisine = serializers.SerializerMethodField()
    deliveryEta = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    menu = serializers.SerializerMethodField()
    mysteryBox = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "tagline",
            "heroImage",
            "rating",
            "cuisine",
            "deliveryEta",
            "location",
            "menu",
            "mysteryBox",
        )

    def get_heroImage(self, obj: Business) -> str | None:
        return obj.hero_image_url or obj.image_url or ""

    def get_rating(self, obj: Business) -> str | None:
        if obj.average_rating is None:
            return ""
        return f"{obj.average_rating:.1f}"

    def get_cuisine(self, obj: Business) -> str | None:
        return obj.category.name if obj.category else ""

    def get_deliveryEta(self, obj: Business) -> str | None:
        return obj.formatted_delivery_eta() or ""

    def get_location(self, obj: Business) -> dict[str, float] | None:
        if obj.latitude is None or obj.longitude is None:
            return None
        return {
            "latitude": float(obj.latitude),
            "longitude": float(obj.longitude),
        }

    def get_menu(self, obj: Business) -> list[dict[str, Any]]:
        sections = obj.menu_sections.prefetch_related("food_items__extra_groups__group__extras")
        return MenuSectionSerializer(sections, many=True).data

    def get_mysteryBox(self, obj: Business) -> dict[str, Any] | None:
        mystery = (
            obj.mystery_boxes.filter(is_active=True)
            .prefetch_related("extra_group_links__group__extras")
            .first()
        )
        if not mystery:
            return None
        return MysteryBoxSerializer(mystery).data


class RestaurantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        fields = (
            "id",
            "name",
            "tagline",
            "description",
            "address",
            "category",
            "latitude",
            "longitude",
            "image_url",
            "hero_image_url",
            "delivery_available",
            "delivery_time_minutes_min",
            "delivery_time_minutes_max",
        )
        read_only_fields = ("id",)

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        min_eta = attrs.get("delivery_time_minutes_min")
        max_eta = attrs.get("delivery_time_minutes_max")
        if min_eta and max_eta and min_eta > max_eta:
            raise serializers.ValidationError(
                {"delivery_time_minutes_max": "Maximum delivery time must be greater than or equal to minimum delivery time."}
            )
        return attrs


class HomeRestaurantCardSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    image = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ("id", "name", "tagline", "image", "background")

    def get_image(self, obj: Business) -> str:
        return obj.hero_image_url or obj.image_url or ""

    def get_background(self, obj: Business) -> str:
        return background_for(obj.pk)


class HomeProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    restaurantId = serializers.CharField(source="business.pk", read_only=True)
    restaurantName = serializers.CharField(source="business.name", read_only=True)
    price = serializers.SerializerMethodField()
    discount = serializers.BooleanField(source="is_discounted", read_only=True)
    percentage = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    shop = serializers.CharField(source="business.name", read_only=True)
    info = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            "id",
            "name",
            "description",
            "price",
            "discount",
            "percentage",
            "restaurantId",
            "restaurantName",
            "shop",
            "background",
            "image",
            "info",
            "modifiers",
        )

    def get_price(self, obj: FoodItem) -> str:
        return obj.price_with_currency()

    def get_percentage(self, obj: FoodItem) -> float | None:
        if obj.discount_percentage is None:
            return None
        return float(obj.discount_percentage)

    def get_background(self, obj: FoodItem) -> str:
        return background_for(obj.pk)

    def get_image(self, obj: FoodItem) -> str:
        return obj.image_url or ""

    def get_info(self, obj: FoodItem) -> str:
        return obj.description or ""

    def get_modifiers(self, obj: FoodItem) -> list[dict[str, Any]]:
        links = obj.extra_groups.select_related("group").all()
        if not links:
            return []
        return ModifierSerializer(links, many=True).data


class RestaurantSummarySerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    score = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = ("id", "name", "score", "background", "image")

    def get_score(self, obj: Business) -> str:
        if obj.average_rating is None:
            return ""
        return f"{obj.average_rating:.1f}"

    def get_background(self, obj: Business) -> str:
        return background_for(obj.pk)

    def get_image(self, obj: Business) -> str:
        return obj.image_url or obj.hero_image_url or ""


class MostOrderedItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    title = serializers.CharField(source="name")
    restaurantId = serializers.CharField(source="business.pk", read_only=True)
    restaurant = serializers.CharField(source="business.name", read_only=True)
    price = serializers.SerializerMethodField()
    eta = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    discount = serializers.BooleanField(source="is_discounted", read_only=True)
    percentage = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            "id",
            "title",
            "restaurantId",
            "restaurant",
            "price",
            "eta",
            "description",
            "background",
            "image",
            "discount",
            "percentage",
            "modifiers",
        )

    def get_price(self, obj: FoodItem) -> str:
        return obj.price_with_currency()

    def get_eta(self, obj: FoodItem) -> str:
        return obj.eta_display() or ""

    def get_background(self, obj: FoodItem) -> str:
        return background_for(f"most-{obj.pk}")

    def get_image(self, obj: FoodItem) -> str:
        return obj.image_url or ""

    def get_percentage(self, obj: FoodItem) -> float | None:
        if obj.discount_percentage is None:
            return None
        return float(obj.discount_percentage)

    def get_modifiers(self, obj: FoodItem) -> list[dict[str, Any]]:
        links = obj.extra_groups.select_related("group").all()
        if not links:
            return []
        return ModifierSerializer(links, many=True).data


class HomeDiscoverySerializer(serializers.Serializer):
    featuredRestaurants = HomeRestaurantCardSerializer(many=True)
    mostOrderedThisWeek = MostOrderedItemSerializer(many=True)
    nearYouRestaurants = RestaurantSummarySerializer(many=True)
    featuredProducts = HomeProductSerializer(many=True)
