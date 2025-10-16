from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.core.validators import MinValueValidator
from django.db import models

CURRENCY_FALLBACK = "NIO"


class MenuSection(models.Model):
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="menu_sections",
    )
    name = models.CharField(max_length=120)
    description = models.TextField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "menu_sections"
        ordering = ("position", "id")

    def __str__(self) -> str:
        return f"{self.business.name} - {self.name}"


class FoodItem(models.Model):
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="food_items",
    )
    section = models.ForeignKey(
        MenuSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="food_items",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=3, default=CURRENCY_FALLBACK)
    preparation_time_minutes = models.PositiveSmallIntegerField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_discounted = models.BooleanField(default=False)
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    original_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "food_items"
        ordering = ("section_id", "name")

    def __str__(self) -> str:
        return f"{self.name} ({self.business.name})"

    def price_with_currency(self) -> str:
        amount = self.price.quantize(Decimal("0.01"))
        symbol = currency_symbol(self.currency)
        return f"{symbol}{amount}"

    def eta_display(self) -> Optional[str]:
        if self.preparation_time_minutes:
            return f"{self.preparation_time_minutes} min"
        return None


class FoodVariant(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="variants")
    name = models.CharField(max_length=100)  # e.g. Small, Large
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "food_variants"
        ordering = ("food_item_id", "id")

    def __str__(self) -> str:
        return f"{self.food_item.name} - {self.name}"


class ExtraGroup(models.Model):
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="extra_groups",
    )
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "extra_groups"
        ordering = ("name",)
        unique_together = ("business", "name")

    def __str__(self) -> str:
        return f"{self.business.name} - {self.name}"


class ExtraItem(models.Model):
    group = models.ForeignKey(ExtraGroup, on_delete=models.CASCADE, related_name="extras")
    name = models.CharField(max_length=100)
    price_delta = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    is_available = models.BooleanField(default=True)

    class Meta:
        db_table = "extra_items"
        ordering = ("group_id", "id")

    def __str__(self) -> str:
        return f"{self.name} (+{self.price_delta})"


class FoodItemExtraGroup(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="extra_groups")
    group = models.ForeignKey(ExtraGroup, on_delete=models.CASCADE, related_name="food_items")
    required = models.BooleanField(default=False)
    min_choices = models.PositiveIntegerField(default=0)
    max_choices = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "food_item_extra_groups"
        unique_together = ("food_item", "group")
        ordering = ("food_item_id", "group_id")

    def __str__(self) -> str:
        return f"{self.food_item.name} -> {self.group.name}"


class FoodTag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = "food_tags"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class FoodItemTag(models.Model):
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name="tags")
    tag = models.ForeignKey(FoodTag, on_delete=models.CASCADE, related_name="food_items")

    class Meta:
        db_table = "food_item_tags"
        unique_together = ("food_item", "tag")

    def __str__(self) -> str:
        return f"{self.food_item.name} -> {self.tag.name}"


class MysteryBox(models.Model):
    business = models.ForeignKey(
        "businesses.Business",
        on_delete=models.CASCADE,
        related_name="mystery_boxes",
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    highlight = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=3, default=CURRENCY_FALLBACK)
    food_item = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mystery_boxes",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_groups = models.ManyToManyField(
        ExtraGroup,
        through="MysteryBoxExtraGroup",
        related_name="mystery_boxes",
        blank=True,
    )

    class Meta:
        db_table = "mystery_boxes"
        ordering = ("business_id", "id")

    def __str__(self) -> str:
        return f"{self.business.name} - {self.title}"

    def price_with_currency(self) -> str:
        amount = self.price.quantize(Decimal("0.01"))
        symbol = currency_symbol(self.currency)
        return f"{symbol}{amount}"


class MysteryBoxExtraGroup(models.Model):
    mystery_box = models.ForeignKey(
        MysteryBox,
        on_delete=models.CASCADE,
        related_name="extra_group_links",
    )
    group = models.ForeignKey(ExtraGroup, on_delete=models.CASCADE, related_name="mystery_box_links")
    required = models.BooleanField(default=False)
    min_choices = models.PositiveIntegerField(default=0)
    max_choices = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "mystery_box_extra_groups"
        unique_together = ("mystery_box", "group")
        ordering = ("mystery_box_id", "group_id")

    def __str__(self) -> str:
        return f"{self.mystery_box.title} -> {self.group.name}"


def currency_symbol(currency_code: str | None) -> str:
    if not currency_code:
        return "C$"
    code = currency_code.upper()
    symbols = {
        "NIO": "C$",
    }
    return symbols.get(code, "C$")
