from django.db import models
from django.conf import settings


class WatchlistItem(models.Model):
    STATUS_CHOICES = [
        ("want_to_watch", "Want to Watch"),
        ("watching", "Watching"),
        ("watched", "Watched"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist"
    )
    tmdb_id = models.IntegerField()
    title = models.CharField(max_length=300)
    poster_path = models.CharField(max_length=200, blank=True, default="")
    release_date = models.CharField(max_length=20, blank=True, default="")
    overview = models.TextField(blank=True, default="")
    vote_average = models.FloatField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="want_to_watch")
    rating = models.IntegerField(default=0)
    review = models.TextField(blank=True, default="")
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "tmdb_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} — {self.title}"