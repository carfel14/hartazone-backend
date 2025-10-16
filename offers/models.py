from __future__ import annotations

from django.db import models


class OfferCategory(models.TextChoices):
    HERO = "hero", "Hero Offer"
    FLASH = "flash", "Flash Deal"
    CURATED = "curated", "Curated Collection"


class Offer(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    image_url = models.URLField(max_length=300)
    savings_label = models.CharField(max_length=50)
    highlight = models.CharField(max_length=200, blank=True)
    tag = models.CharField(max_length=60, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(
        max_length=20, choices=OfferCategory.choices, default=OfferCategory.HERO
    )
    business = models.ForeignKey(
        "businesses.Business", on_delete=models.CASCADE, related_name="offers"
    )
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "offers"
        ordering = ("category", "position", "id")

    def __str__(self) -> str:
        return f"{self.title} ({self.get_category_display()})"


class OfferInterestTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "offer_interest_tags"
        ordering = ("position", "name")

    def __str__(self) -> str:
        return self.name
