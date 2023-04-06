from django import forms
from django.contrib.auth import password_validation
from django.db.models import BLANK_CHOICE_DASH
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(required=True,
                                widget=forms.EmailInput(attrs={'class': 'input input-620px',
                                                               'placeholder': 'Введите Email'}))

    password = forms.CharField(max_length=100, required=True,
                               widget=forms.PasswordInput(attrs={'class': 'input input-620px',
                                                                 'placeholder': 'Введите пароль'}))
    
    
class UserCreateForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)
        # there's a `fields` property now

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'input input-340px',
            'placeholder': 'Введите пароль',
        }),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={
            "autocomplete": "new-password",
            'class': 'input input-400px',
            'placeholder': 'Повторите пароль',
        }),
        strip=False,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['email', 'password1', 'password2']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'input input-460px',
                'placeholder': 'Введите Email',
            }),
        }
        error_messages = {
            'email': {
                'unique': "Пользователь с таким адресом электронной почты уже существует"
            }
        }
        