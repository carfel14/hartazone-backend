from django.contrib import admin

from .models import BusinessCategory, Business, BusinessHours


@admin.register(BusinessCategory)
class BusinessCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


class BusinessHoursInline(admin.TabularInline):
    model = BusinessHours
    extra = 1
    autocomplete_fields = ()
    fields = ("day_of_week", "open_time", "close_time")
    ordering = ("day_of_week",)


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "average_rating",
        "review_count",
        "delivery_time_display",
        "delivery_available",
    )
    list_filter = ("delivery_available", "category")
    search_fields = ("name", "tagline", "description", "address")
    autocomplete_fields = ("category",)
    inlines = [BusinessHoursInline]
    fieldsets = (
        (
            "Informacion general",
            {
                "fields": (
                    "category",
                    "name",
                    "tagline",
                    "description",
                    "image_url",
                    "hero_image_url",
                )
            },
        ),
        (
            "Ubicacion",
            {"fields": ("address", "latitude", "longitude")},
        ),
        (
            "Metricas y entrega",
            {
                "fields": (
                    "average_rating",
                    "review_count",
                    "delivery_available",
                    "delivery_time_minutes_min",
                    "delivery_time_minutes_max",
                )
            },
        ),
    )

    @admin.display(description="Entrega")
    def delivery_time_display(self, obj: Business) -> str | None:
        return obj.formatted_delivery_eta()


@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ("business", "day_of_week", "open_time", "close_time")
    list_filter = ("day_of_week",)
    search_fields = ("business__name",)
    autocomplete_fields = ("business",)
    ordering = ("business__name", "day_of_week")
