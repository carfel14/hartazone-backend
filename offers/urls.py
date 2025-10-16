from rest_framework.routers import DefaultRouter

from .views import OffersViewSet

router = DefaultRouter()
router.register(r"offers", OffersViewSet, basename="offer")

urlpatterns = router.urls
