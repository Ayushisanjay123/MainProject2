from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import MyUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('email', 'first_name', 'last_name')



