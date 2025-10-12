# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class SignUpForm(UserCreationForm):
   
    image = forms.ImageField(required=False)  # حقل الصورة للـ profile
    bio = forms.CharField(widget=forms.Textarea, required=False)  # حقل البايو للـ profile
    class Meta:
        model = User
        fields = ('username',  'password1', 'password2', 'image' ,'bio')  # أضف الحقول التي تريدها هنا
