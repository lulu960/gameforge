
from __future__ import annotations
import os, json, re
from .hf_client import chat_completion, txt2img

def _listify_keywords(keywords: str):
    return [k.strip() for k in keywords.split(",") if k.strip()]

def generate_universe(genre, ambiance, keywords):
    kws = ", ".join(_listify_keywords(keywords))
    prompt = f"Crée un univers concis (5-7 lignes) pour un {genre} ambiance {ambiance}. Mots-clés: {kws}."
    return chat_completion(prompt, max_tokens=300)

def generate_story_3_acts(title, genre, ambiance, keywords, references):
    refs = references or "—"
    prompt = f"Synopsis 3 actes pour '{title}' ({genre}, {ambiance}). Réfs: {refs}. Mots-clés: {keywords}."
    return chat_completion(prompt, max_tokens=500)

def generate_characters(n: int = 3):
    """
    Retourne toujours une LISTE de personnages proprement structurés,
    même si la sortie HF n'est pas du JSON.
    """
    prompt = f"""
    Donne {n} personnages majeurs. Réponds UNIQUEMENT par une liste JSON.
    Chaque objet: 
      - name (str)
      - role (str)
      - abilities (list[str] ou str)
      - motivation (str, 1 phrase)
    Exemple:
    [
      {{"name":"...", "role":"...", "abilities":["...","..."], "motivation":"..."}}
    ]
    """
    raw = chat_completion(prompt, max_tokens=400) or ""

    import json, re
    data = []
    # 1) tentative JSON direct
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            data = parsed
    except Exception:
        pass

    # 2) si échec, tenter d'extraire un bloc [ ... ] n'importe où
    if not data:
        m = re.search(r"\[[\s\S]*\]", raw)
        if m:
            try:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, list):
                    data = parsed
            except Exception:
                pass

    # 3) normalisation + fallback
    out = []
    for ch in (data or [])[:n]:
        abilities = ch.get("abilities", "—")
        # convertir liste -> texte à puces
        if isinstance(abilities, list):
            abilities = "\n".join(str(a) for a in abilities)
        out.append({
            "name": str(ch.get("name", "Inconnu")),
            "role": str(ch.get("role", "—")),
            "abilities": str(abilities or "—"),
            "motivation": str(ch.get("motivation", "—")),
        })

    if not out:
        out = [
            {
                "name": "Alex",
                "role": "Éclaireur",
                "abilities": "Furtivité\nDrones\nParkour",
                "motivation": "Retrouver sa sœur disparue."
            },
            {
                "name": "Mira",
                "role": "Alchimiste",
                "abilities": "Concoctions\nContrôle de zone\nBuffs",
                "motivation": "Rompre un ancien pacte."
            },
            {
                "name": "Rook",
                "role": "Tank",
                "abilities": "Bouclier lourd\nProvocation\nCharge",
                "motivation": "Protéger la cité basse."
            },
        ][:n]
    return out


def generate_locations(ambiance):
    prompt = f"3 lieux emblématiques ambiance {ambiance}, format liste à puces."
    return chat_completion(prompt, max_tokens=200)

def generate_concept_image_urls(genre, ambiance, keywords, title=None, characters=None, locations=None, story=None):
    from django.conf import settings
    media_root = getattr(settings, "MEDIA_ROOT", os.path.join(settings.BASE_DIR,"media"))
    os.makedirs(media_root, exist_ok=True)
    import time
    def save_img(prompt, prefix):
        # Tronquer le prompt à 200 caractères pour éviter l'erreur CLIP
        short_prompt = prompt[:200]
        data = txt2img(short_prompt, width=768, height=512)
        if not data: return None
        timestamp = int(time.time() * 1000)
        filename = f"{prefix}_{timestamp}.png"
        path = os.path.join(media_root, filename)
        with open(path, "wb") as f:
            f.write(data)
        return settings.MEDIA_URL + filename

    # Prompt personnage enrichi
    char_prompt = f"Concept art d'un héros pour un jeu intitulé '{title}' ({genre}, ambiance {ambiance}). "
    if characters and len(characters) > 0:
        ch = characters[0]
        char_prompt += f"Nom: {ch['name']}, Rôle: {ch['role']}, Capacités: {ch['abilities']}, Motivation: {ch['motivation']}. "
    char_prompt += f"Mots-clés: {keywords}. Style cohérent avec l'univers du jeu."

    # Prompt environnement enrichi
    env_prompt = f"Concept art d'un environnement pour '{title}' ({genre}, ambiance {ambiance}). "
    if locations:
        env_prompt += f"Lieux: {locations}. "
    if story:
        env_prompt += f"Scénario: {story[:200]}... "
    env_prompt += f"Mots-clés: {keywords}. Style immersif et cohérent avec le jeu."

    char_url = save_img(char_prompt, "char")
    env_url = save_img(env_prompt, "env")
    if not char_url or not env_url:
        seed = abs(hash((genre, ambiance, keywords))) % 1000
        return (f"https://picsum.photos/seed/char{seed}/640/360", f"https://picsum.photos/seed/env{seed}/1280/720")
    return char_url, env_url

def generate_all(title, genre, ambiance, keywords, references):
    universe = generate_universe(genre, ambiance, keywords)
    story = generate_story_3_acts(title, genre, ambiance, keywords, references)
    locations = generate_locations(ambiance)
    characters = generate_characters()
    char_img, env_img = generate_concept_image_urls(genre, ambiance, keywords)
    return universe, story, locations, characters, char_img, env_img
