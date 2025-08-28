from django import forms
from .models import Game

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ["title", "genre", "ambiance", "keywords", "references", "is_public"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "w-full border rounded p-2", "placeholder":"Titre"}),
            "genre": forms.Select(attrs={"class": "w-full border rounded p-2"}),
            "ambiance": forms.TextInput(attrs={"class": "w-full border rounded p-2", "placeholder":"Ex: Cyberpunk sombre"}),
            "keywords": forms.Textarea(attrs={"class": "w-full border rounded p-2", "rows":3, "placeholder":"boucle temporelle, IA rebelle, ruines anciennes"}),
            "references": forms.Textarea(attrs={"class": "w-full border rounded p-2", "rows":2, "placeholder":"Zelda, Hollow Knight... (facultatif)"}),
        }
