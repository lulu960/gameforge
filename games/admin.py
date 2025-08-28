from django.contrib import admin
from .models import Game, Character, Favorite

class CharacterInline(admin.TabularInline):
    model = Character
    extra = 0

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'genre', 'is_public', 'created_at')
    list_filter = ('genre', 'is_public', 'created_at')
    search_fields = ('title', 'user__username')
    inlines = [CharacterInline]

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'created_at')
    search_fields = ('user__username', 'game__title')
