from .models import *
from django import forms



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

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']

    def __init__(self, *args, **kwargs):
        super(ReviewForm, self).__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'rows': 3,  # Установите желаемое количество строк
            'cols': 40,  # Установите желаемое количество столбцов
            'placeholder': 'Напишите ваш отзыв здесь...',  # Опционально: добавьте placeholder
            'class': 'form-control',  # Добавьте класс Bootstrap для стилизации
        })

