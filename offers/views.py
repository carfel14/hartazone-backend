from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.response import Response

from .models import Offer, OfferCategory, OfferInterestTag
from .serializers import OfferSerializer, OffersResponseSerializer


class OffersViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        offers = (
            Offer.objects.filter(is_active=True)
            .select_related("business")
            .order_by("position", "id")
        )

        interest_tags = list(
            OfferInterestTag.objects.order_by("position", "name").values_list("name", flat=True)
        )

        hero_offers = OfferSerializer(
            offers.filter(category=OfferCategory.HERO), many=True
        ).data
        flash_deals = OfferSerializer(
            offers.filter(category=OfferCategory.FLASH), many=True
        ).data
        curated_collections = OfferSerializer(
            offers.filter(category=OfferCategory.CURATED), many=True
        ).data

        payload = {
            "heroOffers": hero_offers,
            "flashDeals": flash_deals,
            "curatedCollections": curated_collections,
            "interestTags": interest_tags,
        }

        return Response(payload)
