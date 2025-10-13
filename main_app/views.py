from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Flower, Bouquet, Profile, User
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfileForm, UserForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy


# ---------------- Public Pages ----------------
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


# ---------------- Auth ----------------
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            image = form.cleaned_data.get('image')
            bio = form.cleaned_data.get('bio')

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
            next_url = request.GET.get('next') or 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have logged out 🌿')
    return redirect('home')


# ---------------- Bouquets ----------------
def bouquet_list(request):
    bouquets = Bouquet.objects.all()
    return render(request, 'buoquet/bouquet_list.html', {'bouquets': bouquets})

def bouquet_details(request, pk):
    detail = Bouquet.objects.get(id=pk)
    return render(request, 'buoquet/bouquet_details.html', {'detail': detail})


# ---------------- Profile ----------------
@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {'user': request.user})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'user/edit_profile.html'
    model = Profile
    form_class = ProfileForm

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['user_form'] = UserForm(self.request.POST, instance=self.request.user)
        else:
            context['user_form'] = UserForm(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = ProfileForm(request.POST, request.FILES, instance=self.object)
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            # update username
            user = user_form.save(commit=False)

            # update password if provided
            password = user_form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            
            user.save()
            profile_form.save()

            # re-login if password changed
            login(request, user)
            messages.success(request, "Profile updated successfully! 🌸")
            return redirect('profile')

        context = self.get_context_data()
        context['user_form'] = user_form
        return self.render_to_response(context)


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user/delete_account.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user
