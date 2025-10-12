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


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # الصورة والبايو من الفورم
            image = form.cleaned_data.get('image')
            bio = form.cleaned_data.get('bio')

            # نحدث البروفايل اللي انعمل تلقائيًا
            profile = user.profile  
            if image:
                profile.image = image
            if bio:
                profile.bio = bio
            profile.save()

            login(request, user)
            messages.success(request, f'Welcome {user.username}! 🌸')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


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

    