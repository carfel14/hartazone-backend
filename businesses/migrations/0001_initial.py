from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BusinessCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
            options={
                "db_table": "business_categories",
                "verbose_name": "Business Category",
                "verbose_name_plural": "Business Categories",
            },
        ),
        migrations.CreateModel(
            name="Business",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("tagline", models.CharField(blank=True, max_length=180)),
                ("description", models.TextField(blank=True, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("latitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("longitude", models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True)),
                ("image_url", models.URLField(blank=True, max_length=300, null=True)),
                ("hero_image_url", models.URLField(blank=True, max_length=300, null=True)),
                ("average_rating", models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ("review_count", models.PositiveIntegerField(default=0)),
                ("delivery_available", models.BooleanField(default=False)),
                ("delivery_time_minutes_min", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("delivery_time_minutes_max", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="businesses",
                        to="businesses.businesscategory",
                    ),
                ),
            ],
            options={
                "db_table": "businesses",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="BusinessHours",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("day_of_week", models.IntegerField(choices=[(0, "Monday"), (1, "Tuesday"), (2, "Wednesday"), (3, "Thursday"), (4, "Friday"), (5, "Saturday"), (6, "Sunday")])),
                ("open_time", models.TimeField()),
                ("close_time", models.TimeField()),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="hours",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "db_table": "business_hours",
                "ordering": ("business_id", "day_of_week"),
                "unique_together": {("business", "day_of_week")},
            },
        ),
    ]
