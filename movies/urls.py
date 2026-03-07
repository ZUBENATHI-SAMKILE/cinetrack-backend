from django.urls import path
from .views import (
    SearchMoviesView,
    PopularMoviesView,
    MovieDetailView,
    WatchlistView,
    WatchlistItemView,
    UserStatsView,
    MostWatchedView,
)

urlpatterns = [
    # TMDB Proxy
    path("search/", SearchMoviesView.as_view(), name="search-movies"),
    path("popular/", PopularMoviesView.as_view(), name="popular-movies"),
    path("<int:tmdb_id>/", MovieDetailView.as_view(), name="movie-detail"),

    # Watchlist
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/<int:tmdb_id>/", WatchlistItemView.as_view(), name="watchlist-item"),

    # Stats & Most Watched
    path("stats/", UserStatsView.as_view(), name="user-stats"),
    path("most-watched/", MostWatchedView.as_view(), name="most-watched"),
]