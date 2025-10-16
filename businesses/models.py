from django.db import models


class BusinessCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "business_categories"
        verbose_name = "Business Category"
        verbose_name_plural = "Business Categories"

    def __str__(self) -> str:
        return self.name


class Business(models.Model):
    category = models.ForeignKey(
        BusinessCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="businesses",
    )
    name = models.CharField(max_length=150)
    tagline = models.CharField(max_length=180, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    image_url = models.URLField(max_length=300, null=True, blank=True)
    hero_image_url = models.URLField(max_length=300, null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    review_count = models.PositiveIntegerField(default=0)
    delivery_available = models.BooleanField(default=False)
    delivery_time_minutes_min = models.PositiveSmallIntegerField(null=True, blank=True)
    delivery_time_minutes_max = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "businesses"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def formatted_delivery_eta(self) -> str | None:
        if self.delivery_time_minutes_min and self.delivery_time_minutes_max:
            return f"{self.delivery_time_minutes_min}-{self.delivery_time_minutes_max} min"
        if self.delivery_time_minutes_min:
            return f"{self.delivery_time_minutes_min} min"
        if self.delivery_time_minutes_max:
            return f"{self.delivery_time_minutes_max} min"
        return None


class BusinessHours(models.Model):
    DAY_OF_WEEK_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="hours")
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    open_time = models.TimeField()
    close_time = models.TimeField()

    class Meta:
        db_table = "business_hours"
        unique_together = ("business", "day_of_week")
        ordering = ("business_id", "day_of_week")

    def __str__(self) -> str:
        day_label = dict(self.DAY_OF_WEEK_CHOICES).get(self.day_of_week, "Unknown")
        return f"{self.business.name} - {day_label}"
