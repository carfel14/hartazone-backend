from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Business, BusinessCategory


class RestaurantCreateTests(APITestCase):
    def setUp(self):
        self.url = reverse("restaurant-list")
        self.category = BusinessCategory.objects.create(name="Test Cuisine")
        self.User = get_user_model()

    def test_admin_can_create_restaurant(self):
        admin = self.User.objects.create_user(
            email="admin@example.com",
            password="pass1234",
            role=self.User.Roles.ADMIN,
        )
        self.client.force_authenticate(user=admin)

        payload = {
            "name": "New Admin Restaurant",
            "tagline": "Great food",
            "category": self.category.pk,
            "address": "123 Test Street",
            "delivery_available": True,
            "delivery_time_minutes_min": 20,
            "delivery_time_minutes_max": 40,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Business.objects.count(), 1)
        business = Business.objects.get()
        self.assertEqual(business.name, payload["name"])
        self.assertTrue(business.delivery_available)

    def test_non_admin_cannot_create_restaurant(self):
        user = self.User.objects.create_user(
            email="user@example.com",
            password="pass1234",
            role=self.User.Roles.USER,
        )
        self.client.force_authenticate(user=user)

        payload = {
            "name": "Unauthorized Restaurant",
            "category": self.category.pk,
        }

        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Business.objects.count(), 0)
