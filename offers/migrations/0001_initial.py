from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("businesses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OfferInterestTag",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=50, unique=True)),
                ("position", models.PositiveIntegerField(default=0)),
            ],
            options={
                "db_table": "offer_interest_tags",
                "ordering": ("position", "name"),
            },
        ),
        migrations.CreateModel(
            name="Offer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150)),
                ("description", models.TextField()),
                ("image_url", models.URLField(max_length=300)),
                ("savings_label", models.CharField(max_length=50)),
                ("highlight", models.CharField(blank=True, max_length=200)),
                ("tag", models.CharField(blank=True, max_length=60)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("category", models.CharField(choices=[("hero", "Hero Offer"), ("flash", "Flash Deal"), ("curated", "Curated Collection")], default="hero", max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("position", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("business", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="offers", to="businesses.business")),
            ],
            options={
                "db_table": "offers",
                "ordering": ("category", "position", "id"),
            },
        ),
    ]
