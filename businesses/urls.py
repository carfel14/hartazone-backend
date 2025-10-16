from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import HomeDiscoveryViewSet, RestaurantViewSet, api_root

router = DefaultRouter()
router.register(r"restaurants", RestaurantViewSet, basename="restaurant")

home_list = HomeDiscoveryViewSet.as_view({"get": "list"})

urlpatterns = [
    path("", api_root, name="api-root"),
    path("home/", home_list, name="home-discovery"),
]

urlpatterns += router.urls
