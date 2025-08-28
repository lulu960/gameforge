import random

def generate_random_prompt():
    genres = [
        "Fantasy", "Science-Fiction", "Horreur", "Western", "Steampunk", "Mystère", "Thriller", "Aventure", "Romance", "Historique",
        "Cyberpunk", "Space Opera", "Survival", "Noir", "Comédie", "Drame", "Uchronie", "Medieval", "Super-héros", "Magie", "Mythologie",
        "Post-apocalyptique", "Guerre", "Enquête", "Espionnage", "Pirates", "Antiquité", "Contemporain", "Dystopie", "Fantastique", "Paranormal"
    ]
    ambiances = [
        "Sombre", "Lumineux", "Étrange", "Épique", "Dystopique", "Magique", "Post-apocalyptique", "Futuriste", "Gothique", "Pastel",
        "Organique", "Industriel", "Baroque", "Minimaliste", "Coloré", "Désertique", "Aquatique", "Montagneux", "Urbain", "Rural",
        "Onirique", "Psychédélique", "Vintage", "Moderne", "Rustique", "Glacial", "Tropical", "Automnal", "Printanier", "Estival", "Hivernal"
    ]
    titles = [
        "La Porte des Ombres", "L'Éveil des Titans", "Le Chant du Vide", "Les Larmes du Dragon", "Le Labyrinthe des Âmes", "La Cité Engloutie",
        "Le Dernier Oracle", "Les Échos du Passé", "Le Souffle du Néant", "La Couronne de Verre", "Le Pacte des Anciens", "La Nuit des Étoiles",
        "Le Masque du Silence", "La Prophétie Oubliée", "Le Royaume Brisé", "La Danse des Flammes", "Le Sceptre Interdit", "Les Voiles du Temps",
        "Le Trône de Cendres", "La Légende des Sables", "Le Cri du Corbeau", "La Route des Mirages", "Le Miroir Fendu", "La Forêt des Secrets"
    ]
    keywords = [
        "voyage temporel", "artefact perdu", "rébellion", "royaume déchu", "créature mythique", "intelligence artificielle", "malédiction",
        "quête initiatique", "civilisation oubliée", "portail dimensionnel", "pouvoir interdit", "mémoire effacée", "guerre ancestrale",
        "machine vivante", "esprit vengeur", "monde fracturé", "héritage secret", "alliance improbable", "trahison", "sacrifice", "renaissance",
        "épidémie", "mutation", "rituel ancien", "prophétie", "chasse au trésor", "exploration spatiale", "conflit familial", "quête de rédemption"
    ]
    references = [
        "Zelda", "Blade Runner", "Dark Souls", "Stranger Things", "Le Seigneur des Anneaux", "Disco Elysium", "Hollow Knight", "Dune",
        "The Witcher", "Mass Effect", "Game of Thrones", "Star Wars", "Harry Potter", "Bioshock", "Firewatch", "Oxenfree", "Control",
        "Final Fantasy", "Persona", "Death Stranding", "Lost", "Twin Peaks", "Naruto", "Attack on Titan", "Evangelion", "Matrix"
    ]

    genre = random.choice(genres)
    ambiance = random.choice(ambiances)
    title = random.choice(titles)
    selected_keywords = ', '.join(random.sample(keywords, k=2))
    selected_references = ', '.join(random.sample(references, k=2))

    return {
        'genre': genre,
        'ambiance': ambiance,
        'title': title,
        'keywords': selected_keywords,
        'references': selected_references
    }
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


@login_required
def explore_view(request):
    preview = None
    if request.method == 'POST':
        if request.POST.get('delete') == '1':
            # Supprimer le jeu généré
            if 'explore_preview' in request.session:
                del request.session['explore_preview']
            return redirect('games:explore')
        if request.POST.get('regen') == '1':
            # Régénérer un nouveau jeu
            if 'explore_preview' in request.session:
                del request.session['explore_preview']
            # On continue comme une génération normale
        if request.POST.get('save') == '1':
            # Enregistrement du jeu déjà généré
            preview = request.session.get('explore_preview')
            if not preview:
                messages.error(request, "Aucun jeu à enregistrer. Veuillez générer un jeu d'abord.")
                return redirect('games:explore')
            if not _under_daily_limit(request.user):
                messages.error(request, "Limite quotidienne atteinte aujourd'hui.")
                return redirect('games:dashboard')
            game = Game.objects.create(
                user=request.user,
                title=preview['title'], genre=preview['genre'], ambiance=preview['ambiance'], keywords=preview['keywords'],
                references=preview['references'], universe=preview['universe'], story=preview['story'], locations=preview['locations'],
                character_image_url=preview['character_image_url'], environment_image_url=preview['environment_image_url'], is_public=False
            )
            for ch in preview['characters']:
                Character.objects.create(
                    game=game, name=ch['name'], role=ch['role'],
                    abilities=ch['abilities'], motivation=ch['motivation']
                )
            messages.success(request, "Aperçu enregistré dans votre tableau de bord.")
            # Nettoyer la session
            del request.session['explore_preview']
            return redirect('games:detail', pk=game.pk)
        else:
            # Génération du jeu
            from .ai import generate_characters, generate_universe, generate_story_3_acts, generate_locations, generate_concept_image_urls
            prompt = generate_random_prompt()
            genre = prompt['genre']
            ambiance = prompt['ambiance']
            title = prompt['title']
            keywords = prompt['keywords']
            references = prompt['references']

            universe = generate_universe(genre, ambiance, keywords)
            locations = generate_locations(ambiance)
            chars = generate_characters()
            char_img, env_img = generate_concept_image_urls(genre, ambiance, keywords)

            # Harmonisation des noms dans le scénario
            story = generate_story_3_acts(title, genre, ambiance, keywords, references)
            import re
            def replace_names_in_story(story, chars):
                names = [ch['name'] for ch in chars]
                lines = story.splitlines()
                act_pattern = re.compile(r'^(Acte|\*\*|#)', re.IGNORECASE)
                name_pattern = r'\b([A-Z][a-zA-Zéèêëàâäôöûüç]{2,})\b'
                replaced_lines = []
                generated_names = set(names)
                for line in lines:
                    if act_pattern.match(line.strip()):
                        replaced_lines.append(line)
                    else:
                        found = re.findall(name_pattern, line)
                        new_line = line
                        replaceable = [n for n in set(found) if n not in generated_names]
                        for i, old_name in enumerate(replaceable):
                            new_name = names[i % len(names)]
                            new_line = re.sub(rf'\b{re.escape(old_name)}\b', new_name, new_line)
                        replaced_lines.append(new_line)
                return '\n'.join(replaced_lines)
            story = replace_names_in_story(story, chars)

            preview = {
                'title': title, 'genre': genre, 'ambiance': ambiance, 'keywords': keywords, 'references': references,
                'universe': universe, 'story': story, 'locations': locations, 'characters': chars,
                'character_image_url': char_img, 'environment_image_url': env_img,
            }
            request.session['explore_preview'] = preview
    else:
        preview = request.session.get('explore_preview')

    return render(request, 'games/explore.html', {'preview': preview})
