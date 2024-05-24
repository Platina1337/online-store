from .models import *
from django import forms
from django.contrib.auth.models import User
from main.models import BuildingMaterials
class RegistrationProviderForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    first_name = forms.CharField(label='First Name', max_length=150)
    last_name = forms.CharField(label='Last Name', max_length=150)
    city = forms.CharField(label='City', max_length=25)
    passport_number = forms.CharField(label='Passport Number', max_length=6)
    passport_series = forms.CharField(label='Passport Series', max_length=4)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

class AddPostForm(forms.ModelForm):
    class Meta:
        model = BuildingMaterials
        fields = ['title', 'description', 'image', 'price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'class': 'form-control'})