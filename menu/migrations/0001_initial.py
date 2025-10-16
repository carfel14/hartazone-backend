from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("businesses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExtraGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_groups",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "db_table": "extra_groups",
                "ordering": ("name",),
                "unique_together": {("business", "name")},
            },
        ),
        migrations.CreateModel(
            name="FoodItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("description", models.TextField(blank=True, null=True)),
                ("image_url", models.URLField(blank=True, max_length=300, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0.00"))])),
                ("currency", models.CharField(default="NIO", max_length=3)),
                ("preparation_time_minutes", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("is_available", models.BooleanField(default=True)),
                ("is_discounted", models.BooleanField(default=False)),
                ("discount_percentage", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=[MinValueValidator(Decimal("0.00"))])),
                ("original_price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, validators=[MinValueValidator(Decimal("0.00"))])),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="food_items",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "db_table": "food_items",
                "ordering": ("section_id", "name"),
            },
        ),
        migrations.CreateModel(
            name="FoodTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
            ],
            options={
                "db_table": "food_tags",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="MenuSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True, null=True)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="menu_sections",
                        to="businesses.business",
                    ),
                ),
            ],
            options={
                "db_table": "menu_sections",
                "ordering": ("position", "id"),
            },
        ),
        migrations.CreateModel(
            name="MysteryBox",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("description", models.TextField()),
                ("highlight", models.CharField(blank=True, max_length=200)),
                ("image_url", models.URLField(blank=True, max_length=300, null=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0.00"))])),
                ("currency", models.CharField(default="NIO", max_length=3)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mystery_boxes",
                        to="businesses.business",
                    ),
                ),
                (
                    "food_item",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="mystery_boxes",
                        to="menu.fooditem",
                    ),
                ),
            ],
            options={
                "db_table": "mystery_boxes",
                "ordering": ("business_id", "id"),
            },
        ),
        migrations.CreateModel(
            name="ExtraItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("price_delta", models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=7)),
                ("is_available", models.BooleanField(default=True)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extras",
                        to="menu.extragroup",
                    ),
                ),
            ],
            options={
                "db_table": "extra_items",
                "ordering": ("group_id", "id"),
            },
        ),
        migrations.CreateModel(
            name="FoodVariant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10, validators=[MinValueValidator(Decimal("0.00"))])),
                ("is_available", models.BooleanField(default=True)),
                (
                    "food_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="variants",
                        to="menu.fooditem",
                    ),
                ),
            ],
            options={
                "db_table": "food_variants",
                "ordering": ("food_item_id", "id"),
            },
        ),
        migrations.AddField(
            model_name="fooditem",
            name="section",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="food_items",
                to="menu.menusection",
            ),
        ),
        migrations.CreateModel(
            name="MysteryBoxExtraGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("required", models.BooleanField(default=False)),
                ("min_choices", models.PositiveIntegerField(default=0)),
                ("max_choices", models.PositiveIntegerField(default=1)),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mystery_box_links",
                        to="menu.extragroup",
                    ),
                ),
                (
                    "mystery_box",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_group_links",
                        to="menu.mysterybox",
                    ),
                ),
            ],
            options={
                "db_table": "mystery_box_extra_groups",
                "ordering": ("mystery_box_id", "group_id"),
                "unique_together": {("mystery_box", "group")},
            },
        ),
        migrations.AddField(
            model_name="mysterybox",
            name="extra_groups",
            field=models.ManyToManyField(blank=True, related_name="mystery_boxes", through="menu.MysteryBoxExtraGroup", to="menu.extragroup"),
        ),
        migrations.CreateModel(
            name="FoodItemTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "food_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tags",
                        to="menu.fooditem",
                    ),
                ),
                (
                    "tag",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="food_items",
                        to="menu.foodtag",
                    ),
                ),
            ],
            options={
                "db_table": "food_item_tags",
                "unique_together": {("food_item", "tag")},
            },
        ),
        migrations.CreateModel(
            name="FoodItemExtraGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("required", models.BooleanField(default=False)),
                ("min_choices", models.PositiveIntegerField(default=0)),
                ("max_choices", models.PositiveIntegerField(default=1)),
                (
                    "food_item",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="extra_groups",
                        to="menu.fooditem",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="food_items",
                        to="menu.extragroup",
                    ),
                ),
            ],
            options={
                "db_table": "food_item_extra_groups",
                "ordering": ("food_item_id", "group_id"),
                "unique_together": {("food_item", "group")},
            },
        ),
    ]
