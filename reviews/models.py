from django.db import models
from django.conf import settings


class Review(models.Model):
    game = models.ForeignKey(
        'games.Game',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_set'
    )
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('game', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.game} ({self.rating}★)'

    def rating_stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)