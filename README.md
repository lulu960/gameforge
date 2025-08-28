# GameForge — Plateforme Django IA

GameForge est une plateforme web Django permettant de générer des concepts de jeux vidéo avec l'aide de l'IA (Hugging Face, Diffusers, Transformers, etc.).

## 🚀 Installation

```bash
# 1) Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# 2) Installer les dépendances
pip install -r requirements.txt

# 3) Appliquer les migrations
python manage.py migrate

# 4) (Optionnel) Créer un superuser pour l'admin
python manage.py createsuperuser

# 5) Lancer le serveur
python manage.py runserver
```

Accédez à http://127.0.0.1:8000/

## 🧩 Fonctionnalités principales
- Authentification (inscription, connexion, déconnexion)
- Création guidée de jeux vidéo avec formulaire
- Génération IA : univers, scénario (3 actes), lieux, personnages, images conceptuelles
- Exploration libre : génération aléatoire, sauvegarde si connecté
- Tableau de bord personnel, page de détail, favoris
- Toggle Public/Privé pour chaque jeu
- UI moderne avec Tailwind CSS
- Limite quotidienne de génération par utilisateur (modifiable via `GAMEFORGE_DAILY_LIMIT`)

## 🎮 Modèle de données
- **Game** : titre, genre (30+ genres), ambiance, mots-clés, références, univers, histoire, lieux, images conceptuelles, visibilité
- **Character** : nom, rôle, capacités, motivation
- **Favorite** : favoris utilisateur

## 🤖 Génération IA
- Utilise Hugging Face InferenceClient pour générer le texte et les images (Stable Diffusion, CLIP, etc.)
- Prompts enrichis et aléatoires pour chaque génération
- Harmonisation des noms de personnages dans le scénario
- Images conceptuelles générées avec contexte du jeu

## 📦 Dépendances principales
- Django
- Pillow
- requests
- python-dotenv
- torch, torchvision, torchaudio (GPU support)
- diffusers, transformers, huggingface_hub

## 🖼️ Images conceptuelles
- Par défaut : placeholders via Picsum
- Pour la production : configurez Hugging Face / Stable Diffusion

## 🔒 Authentification & Limites
- Accès à l'exploration et à la sauvegarde uniquement pour les utilisateurs connectés
- Limite quotidienne configurable via variable d'environnement

## 📝 Exemple d'utilisation
- Créez un compte
- Explorez ou créez un jeu via le formulaire
- Visualisez le scénario, les personnages, les images générées
- Ajoutez aux favoris, basculez la visibilité

## 📄 Licence
Projet pédagogique — libre d'utilisation et de modification.
