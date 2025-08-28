from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from .models import Game, Character, Favorite
from .forms import GameForm
from .ai import generate_all, generate_all as ai_generate_all

def home_view(request):
    games = Game.objects.filter(is_public=True).order_by('-created_at')
    return render(request, 'games/home.html', {'games': games})

@login_required
def dashboard_view(request):
    games = Game.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'games/dashboard.html', {'games': games})

def _under_daily_limit(user):
    today = timezone.now().date()
    count_today = Game.objects.filter(user=user, created_at__date=today).count()
    return count_today < settings.GAMEFORGE_DAILY_LIMIT

@login_required
def create_game_view(request):
    if request.method == 'POST':
        if not _under_daily_limit(request.user):
            messages.error(request, "Limite quotidienne de génération atteinte. Réessayez demain 🙏")
            return redirect('games:dashboard')

        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save(commit=False)
            game.user = request.user

            universe, story, locations, characters, char_img, env_img = ai_generate_all(
                game.title, game.genre, game.ambiance, game.keywords, game.references
            )
            game.universe = universe
            game.story = story
            game.locations = locations
            game.character_image_url = char_img
            game.environment_image_url = env_img
            game.save()

            for ch in characters:
                Character.objects.create(
                    game=game, name=ch['name'], role=ch['role'],
                    abilities=ch['abilities'], motivation=ch['motivation']
                )
            messages.success(request, "Jeu généré avec succès 🎉")
            return redirect('games:detail', pk=game.pk)
    else:
        form = GameForm()
    return render(request, 'games/game_form.html', {'form': form})

def game_detail_view(request, pk):
    game = get_object_or_404(Game, pk=pk)
    # En privé: seulement l'auteur peut voir
    if not game.is_public and (not request.user.is_authenticated or request.user != game.user):
        messages.error(request, "Ce jeu est privé.")
        return redirect('home')
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, game=game).exists()
    return render(request, 'games/detail.html', {'game': game, 'is_favorite': is_favorite})

@login_required
def add_favorite_view(request, pk):
    game = get_object_or_404(Game, pk=pk)
    Favorite.objects.get_or_create(user=request.user, game=game)
    messages.success(request, "Ajouté aux favoris ⭐")
    return redirect('games:detail', pk=pk)

@login_required
def remove_favorite_view(request, pk):
    game = get_object_or_404(Game, pk=pk)
    Favorite.objects.filter(user=request.user, game=game).delete()
    messages.info(request, "Retiré des favoris.")
    return redirect('games:detail', pk=pk)

@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('game').order_by('-created_at')
    return render(request, 'games/favorites.html', {'favorites': favorites})

@login_required
def toggle_privacy_view(request, pk):
    game = get_object_or_404(Game, pk=pk, user=request.user)
    game.is_public = not game.is_public
    game.save()
    messages.info(request, f"Visibilité changée: {'Public' if game.is_public else 'Privé'}")
    return redirect('games:dashboard')

def explore_view(request):
    # Exploration libre: génère un jeu aléatoire SANS formulaire
    # Si user connecté: propose de sauvegarder
    from .ai import generate_characters, generate_universe, generate_story_3_acts, generate_locations, generate_concept_image_urls
    import random
    genres = [c[0] for c in Game.GENRES]
    genre = random.choice(genres)
    ambiance = random.choice(["Cyberpunk nébuleux", "Dark Fantasy gothique", "Onirique pastel", "Post-apo organique"])
    title = random.choice(["Echoes of Glass", "Hollow Lines", "Sepia Crown", "Neon Pilgrims"])
    keywords = "boucle temporelle, IA rebelle, ruines anciennes"
    references = "Zelda, Hollow Knight, Disco Elysium"

    universe = generate_universe(genre, ambiance, keywords)
    story = generate_story_3_acts(title, genre, ambiance, keywords, references)
    locations = generate_locations(ambiance)
    chars = generate_characters()
    char_img, env_img = generate_concept_image_urls(genre, ambiance, keywords)

    preview = {
        'title': title, 'genre': genre, 'ambiance': ambiance, 'keywords': keywords, 'references': references,
        'universe': universe, 'story': story, 'locations': locations, 'characters': chars,
        'character_image_url': char_img, 'environment_image_url': env_img,
    }

    if request.method == 'POST' and request.user.is_authenticated:
        if not _under_daily_limit(request.user):
            messages.error(request, "Limite quotidienne atteinte aujourd'hui.")
            return redirect('games:dashboard')
        game = Game.objects.create(
            user=request.user, title=title, genre=genre, ambiance=ambiance, keywords=keywords,
            references=references, universe=universe, story=story, locations=locations,
            character_image_url=char_img, environment_image_url=env_img, is_public=False
        )
        for ch in chars:
            Character.objects.create(
                game=game, name=ch['name'], role=ch['role'],
                abilities=ch['abilities'], motivation=ch['motivation']
            )
        messages.success(request, "Aperçu enregistré dans votre tableau de bord.")
        return redirect('games:detail', pk=game.pk)

    return render(request, 'games/explore.html', {'preview': preview})
