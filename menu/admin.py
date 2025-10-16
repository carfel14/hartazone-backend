from django.contrib import admin

from .models import (
    ExtraGroup,
    ExtraItem,
    FoodItem,
    FoodItemExtraGroup,
    FoodVariant,
    MenuSection,
    MysteryBox,
    MysteryBoxExtraGroup,
)


class FoodVariantInline(admin.TabularInline):
    model = FoodVariant
    extra = 0
    fields = ("name", "price", "is_available")
    ordering = ("name",)


class FoodItemExtraGroupInline(admin.TabularInline):
    model = FoodItemExtraGroup
    extra = 0
    autocomplete_fields = ("group",)
    fields = ("group", "required", "min_choices", "max_choices")


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "business",
        "section",
        "price",
        "is_available",
        "is_discounted",
    )
    list_filter = ("business", "section", "is_available", "is_discounted")
    search_fields = ("name", "description")
    autocomplete_fields = ("business", "section")
    inlines = [FoodVariantInline, FoodItemExtraGroupInline]
    ordering = ("business__name", "section__position", "name")


class FoodItemInline(admin.TabularInline):
    model = FoodItem
    extra = 0
    fields = ("name", "price", "is_available", "is_discounted")
    show_change_link = True
    ordering = ("name",)


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ("name", "business", "position")
    list_filter = ("business",)
    search_fields = ("name", "description", "business__name")
    autocomplete_fields = ("business",)
    inlines = [FoodItemInline]
    ordering = ("business__name", "position")


class ExtraItemInline(admin.TabularInline):
    model = ExtraItem
    extra = 0
    fields = ("name", "price_delta", "is_available")
    ordering = ("name",)


@admin.register(ExtraGroup)
class ExtraGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "business")
    list_filter = ("business",)
    search_fields = ("name", "business__name")
    autocomplete_fields = ("business",)
    inlines = [ExtraItemInline]
    ordering = ("business__name", "name")


@admin.register(ExtraItem)
class ExtraItemAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "price_delta", "is_available")
    list_filter = ("group__business", "group")
    search_fields = ("name", "group__name")
    autocomplete_fields = ("group",)
    ordering = ("group__business__name", "group__name", "name")


class MysteryBoxExtraGroupInline(admin.TabularInline):
    model = MysteryBoxExtraGroup
    extra = 0
    autocomplete_fields = ("group",)
    fields = ("group", "required", "min_choices", "max_choices")


@admin.register(MysteryBox)
class MysteryBoxAdmin(admin.ModelAdmin):
    list_display = ("title", "business", "price", "is_active")
    list_filter = ("business", "is_active")
    search_fields = ("title", "description")
    autocomplete_fields = ("business", "food_item")
    inlines = [MysteryBoxExtraGroupInline]
    ordering = ("business__name", "title")
