from __future__ import annotations

from rest_framework import serializers

from .models import Offer


class OfferSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source="image_url")
    savingsLabel = serializers.CharField(source="savings_label")
    restaurantId = serializers.CharField(source="business.pk", read_only=True)
    restaurantName = serializers.CharField(source="business.name", read_only=True)
    expiresIn = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = (
            "id",
            "title",
            "description",
            "image",
            "savingsLabel",
            "restaurantId",
            "restaurantName",
            "highlight",
            "tag",
            "expiresIn",
        )

    def get_expiresIn(self, obj: Offer) -> str:
        if not obj.expires_at:
            return ""
        return obj.expires_at.isoformat()


class OffersResponseSerializer(serializers.Serializer):
    heroOffers = OfferSerializer(many=True)
    flashDeals = OfferSerializer(many=True)
    curatedCollections = OfferSerializer(many=True)
    interestTags = serializers.ListField(child=serializers.CharField())
