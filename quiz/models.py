from django.db import models

class Movie(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    release_year = models.IntegerField()
    genre = models.CharField(max_length=100, blank=True, null=True)
    hints = models.JSONField(default=list)  # Store hints as a JSON field

    def __str__(self):
        return self.title
    
class Leaderboard(models.Model):
    username = models.CharField(max_length=100)
    score = models.IntegerField()

    class Meta:
        ordering = ['-score']  # Sort by highest score