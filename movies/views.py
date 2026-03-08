import requests
from django.conf import settings
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import WatchlistItem
from .serializers import WatchlistItemSerializer, WatchlistItemCreateSerializer

TMDB_BASE = "https://api.themoviedb.org/3"


def tmdb_get(endpoint, params=None):
    p = {"api_key": settings.TMDB_API_KEY, "language": "en-US"}
    if params:
        p.update(params)
    try:
        res = requests.get(f"{TMDB_BASE}{endpoint}", params=p, timeout=10)
        print(f"TMDB URL: {res.url}")
        print(f"TMDB Status: {res.status_code}")
        print(f"TMDB Response: {res.text[:200]}")
        return res.json()
    except Exception as e:
        print(f"TMDB Error: {e}")
        return {}


class SearchMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response({"error": "Query parameter 'q' is required"}, status=400)
        data = tmdb_get("/search/movie", {"query": query})
        return Response(data.get("results", []))


class PopularMoviesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        print(f"TMDB API KEY in use: {settings.TMDB_API_KEY}")
        data = tmdb_get("/movie/popular")
        results = data.get("results", [])
        print(f"Results count: {len(results)}")
        return Response(results)


class MovieDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, tmdb_id):
        data = tmdb_get(f"/movie/{tmdb_id}", {"append_to_response": "credits"})
        return Response(data)


class WatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WatchlistItem.objects.filter(user=request.user)
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = WatchlistItemSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        tmdb_id = request.data.get("tmdb_id")
        if WatchlistItem.objects.filter(user=request.user, tmdb_id=tmdb_id).exists():
            return Response({"error": "Movie already in watchlist"}, status=status.HTTP_409_CONFLICT)
        serializer = WatchlistItemCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            item = serializer.save()
            return Response(WatchlistItemSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WatchlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, tmdb_id):
        try:
            return WatchlistItem.objects.get(user=request.user, tmdb_id=tmdb_id)
        except WatchlistItem.DoesNotExist:
            return None

    def get(self, request, tmdb_id):
        item = self.get_object(request, tmdb_id)
        if not item:
            return Response({"in_list": False})
        return Response({"in_list": True, **WatchlistItemSerializer(item).data})

    def patch(self, request, tmdb_id):
        item = self.get_object(request, tmdb_id)
        if not item:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = WatchlistItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, tmdb_id):
        item = self.get_object(request, tmdb_id)
        if not item:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = WatchlistItem.objects.filter(user=request.user)
        rated = qs.filter(rating__gt=0)
        avg = rated.aggregate(avg=Avg("rating"))["avg"] or 0
        return Response({
            "total": qs.count(),
            "watched": qs.filter(status="watched").count(),
            "watching": qs.filter(status="watching").count(),
            "want_to_watch": qs.filter(status="want_to_watch").count(),
            "avg_rating": round(avg, 1),
        })


class MostWatchedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top = (
            WatchlistItem.objects
            .values("tmdb_id", "title", "poster_path", "release_date", "vote_average")
            .annotate(watch_count=Count("id"))
            .order_by("-watch_count")[:20]
        )
        return Response(list(top))