# GameForge — TP Django

Plateforme Django pour générer des concepts de jeux vidéo (placeholders IA).

## ⚙️ Installation rapide

```bash
# 1) Créer un venv
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2) Installer les dépendances
pip install -r requirements.txt

# 3) Migrations
python manage.py migrate

# (Optionnel) Créer un superuser pour l'admin
python manage.py createsuperuser

# 4) Lancer
python manage.py runserver
```

Ouvrez http://127.0.0.1:8000/

## 🌟 Fonctionnalités
- Authentification (inscription, connexion, déconnexion)
- Formulaire guidé de création de jeu
- Génération de contenu (placeholders IA)
- Exploration libre (génération aléatoire, sauvegarde si connecté)
- Tableau de bord perso, page de détail, favoris
- Toggle Public/Privé
- UI Tailwind via CDN

## 🔧 Paramètres
- Limite quotidienne de génération par utilisateur (défaut: 10) :
  - Variable d'environnement `GAMEFORGE_DAILY_LIMIT`

## 🖼️ Images conceptuelles
- Actuellement: placeholders via Picsum (seeds). Remplacez par un appel Stable Diffusion / Hugging Face.
