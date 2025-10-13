from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile , Bouquet, BouquetFlower , Flower
from django.forms import inlineformset_factory


class SignUpForm(UserCreationForm):
    image = forms.ImageField(required=False)  
    bio = forms.CharField(widget=forms.Textarea, required=False)  

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'image', 'bio')  

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class UserForm(forms.ModelForm):
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('username',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 or p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class BouquetForm(forms.ModelForm):
    class Meta:
        model = Bouquet
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class FlowersSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for flower in Flower.objects.all():
            self.fields[f'flower_{flower.id}'] = forms.IntegerField(
                label=flower.name,
                min_value=0,
                required=False,
                initial=0,
                widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity'})
            )