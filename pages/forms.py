from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.forms import ModelForm

from .models import CustomUser
from django.conf import settings


class CreateCustomUserForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), label='')
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email'}), label='')
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name'}), label='')
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name'}), label='')
    birthday = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Birthday (day-month-year)'}),
                               input_formats=settings.DATE_INPUT_FORMATS, label='')
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label='')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}), label='')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'birthday', 'password1', 'password2']


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}), label='')
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}), label='')


class CustomUserInfoForm(ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'readonly': 'true'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email', 'readonly': 'true'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First name', 'readonly': 'true'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last name', 'readonly': 'true'}))
    birthday = forms.DateField(widget=forms.DateInput(attrs={'placeholder': 'Phone', 'readonly': 'true'}))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'birthday']
