from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    GENRES = [
        ("RPG", "RPG"),
        ("FPS", "FPS"),
        ("MV", "Metroidvania"),
        ("VN", "Visual Novel"),
        ("PLAT", "Platformer"),
        ("STR", "Strategy"),
        ("ACT", "Action-Adventure"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=20, choices=GENRES, default="RPG")
    ambiance = models.CharField(max_length=200, help_text="Ex: Cyberpunk, Dark Fantasy, Onirique...")
    keywords = models.TextField(help_text="Mots-clés séparés par des virgules")
    references = models.TextField(blank=True, null=True)

    # Generated content
    universe = models.TextField(blank=True, null=True)
    story = models.TextField(blank=True, null=True)  # 3 actes
    locations = models.TextField(blank=True, null=True)

    # Concept art (URLs)
    character_image_url = models.URLField(blank=True, null=True)
    environment_image_url = models.URLField(blank=True, null=True)

    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Character(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120)
    abilities = models.TextField()
    motivation = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.role})"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')
