from rest_framework import serializers
from .models import WatchlistItem


class WatchlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = [
            "id", "tmdb_id", "title", "poster_path", "release_date",
            "overview", "vote_average", "status", "rating", "review",
            "added_at", "updated_at",
        ]
        read_only_fields = ["id", "added_at", "updated_at"]


class WatchlistItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchlistItem
        fields = [
            "tmdb_id", "title", "poster_path", "release_date",
            "overview", "vote_average", "status", "rating", "review",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return WatchlistItem.objects.create(user=user, **validated_data)


class WatchlistStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    watched = serializers.IntegerField()
    watching = serializers.IntegerField()
    want_to_watch = serializers.IntegerField()
    avg_rating = serializers.FloatField()