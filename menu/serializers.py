from __future__ import annotations

from decimal import Decimal
from typing import Any

from rest_framework import serializers

from .models import (
    ExtraItem,
    ExtraGroup,
    FoodItem,
    FoodItemExtraGroup,
    MenuSection,
    MysteryBox,
    MysteryBoxExtraGroup,
    currency_symbol,
)


class ExtraItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    label = serializers.CharField(source="name")
    priceDelta = serializers.SerializerMethodField()

    class Meta:
        model = ExtraItem
        fields = ("id", "label", "priceDelta")

    def get_priceDelta(self, obj: ExtraItem) -> float:
        return float(obj.price_delta or Decimal("0.00"))


class ModifierSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="group.pk", read_only=True)
    name = serializers.CharField(source="group.name", read_only=True)
    options = serializers.SerializerMethodField()

    class Meta:
        model = FoodItemExtraGroup
        fields = ("id", "name", "options")

    def get_options(self, obj: FoodItemExtraGroup) -> list[dict[str, Any]]:
        extras = obj.group.extras.filter(is_available=True)
        return ExtraItemSerializer(extras, many=True).data


class FoodItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    price = serializers.SerializerMethodField()
    eta = serializers.SerializerMethodField()
    discount = serializers.BooleanField(source="is_discounted", read_only=True)
    percentage = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            "id",
            "name",
            "description",
            "price",
            "image",
            "eta",
            "discount",
            "percentage",
            "modifiers",
        )

    def get_price(self, obj: FoodItem) -> str:
        return obj.price_with_currency()

    def get_eta(self, obj: FoodItem) -> str | None:
        return obj.eta_display()

    def get_percentage(self, obj: FoodItem) -> float | None:
        if obj.discount_percentage is None:
            return None
        return float(obj.discount_percentage)

    def get_image(self, obj: FoodItem) -> str:
        return obj.image_url or ""

    def get_modifiers(self, obj: FoodItem) -> list[dict[str, Any]]:
        links = obj.extra_groups.select_related("group").all()
        if not links:
            return []
        serialized = ModifierSerializer(links, many=True)
        return serialized.data


class MenuSectionSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    title = serializers.CharField(source="name")
    items = serializers.SerializerMethodField()

    class Meta:
        model = MenuSection
        fields = ("id", "title", "description", "items")

    def get_items(self, obj: MenuSection) -> list[dict[str, Any]]:
        items = obj.food_items.filter(is_available=True).select_related("section", "business")
        return FoodItemSerializer(items, many=True).data


class MysteryBoxModifierSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="group.pk", read_only=True)
    name = serializers.CharField(source="group.name", read_only=True)
    options = serializers.SerializerMethodField()

    class Meta:
        model = MysteryBoxExtraGroup
        fields = ("id", "name", "options")

    def get_options(self, obj: MysteryBoxExtraGroup) -> list[dict[str, Any]]:
        extras = obj.group.extras.filter(is_available=True)
        return ExtraItemSerializer(extras, many=True).data


class MysteryBoxSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = MysteryBox
        fields = (
            "id",
            "title",
            "description",
            "highlight",
            "price",
            "image",
            "modifiers",
        )

    def get_price(self, obj: MysteryBox) -> str:
        return obj.price_with_currency()

    def get_image(self, obj: MysteryBox) -> str:
        return obj.image_url or ""

    def get_modifiers(self, obj: MysteryBox) -> list[dict[str, Any]]:
        links = obj.extra_group_links.select_related("group").all()
        if not links:
            return []
        return MysteryBoxModifierSerializer(links, many=True).data


class FoodItemDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="pk", read_only=True)
    price = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    eta = serializers.SerializerMethodField()
    restaurantId = serializers.CharField(source="business.pk", read_only=True)
    restaurantName = serializers.CharField(source="business.name", read_only=True)
    discount = serializers.BooleanField(source="is_discounted", read_only=True)
    percentage = serializers.SerializerMethodField()
    modifiers = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = (
            "id",
            "name",
            "description",
            "price",
            "image",
            "info",
            "eta",
            "restaurantId",
            "restaurantName",
            "discount",
            "percentage",
            "modifiers",
        )

    def get_price(self, obj: FoodItem) -> str:
        return obj.price_with_currency()

    def get_image(self, obj: FoodItem) -> str | None:
        return obj.image_url or ""

    def get_info(self, obj: FoodItem) -> str | None:
        return obj.description or ""

    def get_eta(self, obj: FoodItem) -> str | None:
        return obj.eta_display() or ""

    def get_percentage(self, obj: FoodItem) -> float | None:
        if obj.discount_percentage is None:
            return None
        return float(obj.discount_percentage)

    def get_modifiers(self, obj: FoodItem) -> list[dict[str, Any]]:
        links = obj.extra_groups.select_related("group").all()
        if not links:
            return []
        return ModifierSerializer(links, many=True).data
