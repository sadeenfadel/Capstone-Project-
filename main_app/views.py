from django.shortcuts import render , redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Flower, Bouquet , Profile , User
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# undertanding every part of this :) 
def signup_view(request):
    if request.method == 'POST':     # the user sent his data 
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():        # everything is ok with data 
            user = form.save()     # saving the user to the database  with his User info // here the signal will create the profile automatically
            image = form.cleaned_data.get('image')   # get the image and bio from the form 
            bio = form.cleaned_data.get('bio')       # cleaned_data is dictionary of all the fields in the form we cant call this before is_valid()

            profile = user.profile      # get the profile related to this user
            if image:                   # if the user uploaded an image
                profile.image = image   # set the profile image to the uploaded image
            if bio:                     # if the user wrote a bio
                profile.bio = bio       # set the profile bio to the written bio
            profile.save()              # save the profile to the database

            login(request, user)        # log the user in  no need to enter his data again in login form  (user is the user object that we just created)
            messages.success(request, f'Welcome {user.username}! 🌸')     
            return redirect('home')
    else:     # the user is visiting the page
        form = SignUpForm()     
    return render(request, 'registration/signup.html', {'form': form})   # render the form in the template with the context 


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back {user.username}! 💐')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have logged out 🌿')
    return redirect('home')



def bouquet_list(request):
    bouquets = Bouquet.objects.all()  
    return render(request, 'buoquet/bouquet_list.html', {'bouquets': bouquets})

def bouquet_details(request, pk):
    detail = Bouquet.objects.get(id=pk)
    return render(request, 'buoquet/bouquet_details.html', {'detail': detail})

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user':request.user})

    