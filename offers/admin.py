from django.contrib import admin

from .models import Offer, OfferInterestTag


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "business", "category", "savings_label", "is_active", "position")
    list_filter = ("category", "is_active", "business")
    search_fields = ("title", "description", "business__name")
    autocomplete_fields = ("business",)
    ordering = ("category", "position")


@admin.register(OfferInterestTag)
class OfferInterestTagAdmin(admin.ModelAdmin):
    list_display = ("name", "position")
    ordering = ("position", "name")
    search_fields = ("name",)
