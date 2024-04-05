from .models import *
from django import forms

class AddPostModel(forms.ModelForm):
    class Meta:
        model = BuildingMaterials
        fields = ['title', 'description', 'image', 'price']

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

# 6tn47mrmxx76i9ooh4mbb8uwezrufedg34xk9kxo

