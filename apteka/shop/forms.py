from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class CustomRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, help_text=None,
                                 widget=forms.TextInput(attrs={'class': 'registerinput'}))
    last_name = forms.CharField(max_length=50, required=True, help_text=None,
                                widget=forms.TextInput(attrs={'class': 'registerinput'}))
    email = forms.EmailField(required=True, help_text=None, widget=forms.TextInput(
        attrs={'class': 'registerinput'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1']

    def __init__(self, *args, **kwargs):
        super(CustomRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Nazwa użytkownika"
        self.fields['email'].label = "Email"
        self.fields['first_name'].label = "Imię"
        self.fields['last_name'].label = "Nazwisko"
        self.fields['password1'].label = "Hasło"
        self.fields['password2'].label = "Powtórz hasło"

        self.fields['username'].help_text = None
        self.fields['email'].help_text = None
        self.fields['first_name'].help_text = None
        self.fields['last_name'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        self.fields['username'].widget.attrs['class'] = 'registerinput'
        self.fields['password1'].widget.attrs['class'] = 'registerinput'
        self.fields['password2'].widget.attrs['class'] = 'registerinput'


class ItemSearchForm(forms.Form):
    szukaj = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={'placeholder': 'Wyszukaj'}))