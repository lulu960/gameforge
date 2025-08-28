from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


from django.contrib.auth.forms import UserChangeForm

class ProfileUpdateForm(UserChangeForm):
    password = None  # On ne modifie pas le mot de passe ici
    class Meta:
        model = User
        fields = ("username", "email",)
