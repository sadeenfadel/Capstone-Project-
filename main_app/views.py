from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import Flower, Bouquet, Profile, User ,  BouquetFlower , Order , OrderBouquet
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfileForm, UserForm , BouquetForm, FlowersSelectionForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.forms import modelform_factory

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
            if user.is_superuser:
                return redirect('admin_dashboard')  
            else:
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
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    
    return render(request, 'buoquet/bouquet_list.html', {
        'bouquets': bouquets,
        'base_template': base_template
    })

def bouquet_details(request, pk):
    detail = Bouquet.objects.get(id=pk)
    return render(request, 'buoquet/bouquet_details.html', {'detail': detail})

def superuser_required(user):
    return user.is_superuser

@login_required
@user_passes_test(superuser_required)
def create_bouquet(request):
    if request.method == 'POST':
        bouquet_form = BouquetForm(request.POST, request.FILES)
        flowers_form = FlowersSelectionForm(request.POST)

        if bouquet_form.is_valid() and flowers_form.is_valid():
            bouquet = bouquet_form.save(commit=False)
            bouquet.user = request.user
            bouquet.save()

          
            for field_name, quantity in flowers_form.cleaned_data.items():
                if quantity and quantity > 0:
                    flower_id = int(field_name.split('_')[1])
                    BouquetFlower.objects.create(
                        bouquet=bouquet,
                        flower_id=flower_id,
                        quantity=quantity
                    )

            messages.success(request, "Bouquet created successfully! 🌸")
            return redirect('bouquet_list')
    else:
        bouquet_form = BouquetForm()
        flowers_form = FlowersSelectionForm()

    return render(request, 'buoquet/create_bouquet.html', {
        'bouquet_form': bouquet_form,
        'flowers_form': flowers_form,
        'base_template': 'admin_base.html'
    })
# ---------------- Edit Bouquet ----------------
@login_required
@user_passes_test(superuser_required)
def edit_bouquet(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk)
    BouquetForm = modelform_factory(Bouquet, fields=['name', 'image'])
    
    if request.method == 'POST':
        form = BouquetForm(request.POST, request.FILES, instance=bouquet)
        if form.is_valid():
            form.save()
            messages.success(request, "Bouquet updated successfully! 🌸")
            return redirect('bouquet_detail', pk=bouquet.pk)
    else:
        form = BouquetForm(instance=bouquet)
    
    return render(request, 'buoquet/edit_bouquet.html', {
        'form': form,
        'bouquet': bouquet,
        'base_template': 'admin_base.html'
    })


# ---------------- Delete Bouquet ----------------
@login_required
@user_passes_test(superuser_required)
def delete_bouquet(request, pk):
    bouquet = get_object_or_404(Bouquet, pk=pk)
    
    if request.method == 'POST':
        bouquet.delete()
        messages.success(request, "Bouquet deleted successfully! 💐")
        return redirect('bouquet_list')
    
    return render(request, 'buoquet/delete_bouquet.html', {
        'bouquet': bouquet,
        'base_template': 'admin_base.html'
    })
# ---------------- Profile ----------------
@login_required
def profile_view(request):
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'user/profile.html', {
        'user': request.user,
        'base_template': base_template
    })
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'user/edit_profile.html'  # <--- حددنا القالب هنا

    def get_object(self, queryset=None):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserForm(
            self.request.POST if self.request.POST else None, 
            instance=self.request.user
        )
        # نرسل للـ template القالب الأساسي (لليوزر أو الادمن)
        context['base_template'] = 'admin_base.html' if self.request.user.is_superuser else 'base.html'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        profile_form = ProfileForm(request.POST, request.FILES, instance=self.object)
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            user = user_form.save(commit=False)
            password = user_form.cleaned_data.get('password1')
            if password:
                user.set_password(password)
            user.save()
            profile_form.save()
            login(request, user)
            messages.success(request, "Profile updated successfully! 🌸")

            return redirect('admin_dashboard' if user.is_superuser else 'profile')

        context = self.get_context_data()
        context['user_form'] = user_form
        return self.render_to_response(context)


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user/delete_account.html'  # <--- حددنا القالب هنا

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['base_template'] = 'admin_base.html' if self.request.user.is_superuser else 'base.html'
        return context

    def get_success_url(self):
        return reverse_lazy('admin_dashboard' if self.request.user.is_superuser else 'home')

@login_required
def profile_view(request):
    return render(request, 'user/profile.html', {
        'user': request.user,
        'base_template': 'admin_base.html' if request.user.is_superuser else 'base.html'
    })

# ---------------- Admin Dashboard ----------------
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admins only.")
        return redirect('home')
    
    users = User.objects.all()
    bouquets = Bouquet.objects.all()
    flowers = Flower.objects.all()
    oders = Order.objects.all()
    context = {
        'users': users,
        'bouquets': bouquets,
        'flowers': flowers,
        'orders':oders,
    }
    return render(request, 'admin/admin_dashboard.html', context)



#-------------------------order-------------------------------------
@login_required
def create_order(request , pk):
    # 1 . get the bouquet with pk = pk 
    bquet = get_object_or_404(Bouquet , pk=pk) 
    
    # here iam creating order so POST 
    if request.method == 'POST' :  # the user sent the order form
        qnt =  int(request.POST.get('quantity'))  # the quantity user inserted 
        total_price = bquet.total_price * qnt 
        order = Order.objects.create(user=request.user , total_price =total_price )
        OrderBouquet.objects.create(order =order , bouquet = bquet , quantity=qnt , bouquet_name = bquet.name)
        messages.success(request, f"Your order for {bquet.name} x{qnt} has been placed! 🌸")
        return redirect('order_dtail'  , pk = order.id)
    return render (request , 'order/create_order.html' , {'boq' : bquet}) # here we render the page passing to it the boq details 


@login_required
def order_details(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)   # returning the order for specific order and user
    order_items = order.orderbouquet_set.all()  # جميع البوكيهات داخل الأوردر
    for item in order_items:
       item.subtotal = item.bouquet.total_price * item.quantity

    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'order/order_detail.html', {'order': order, 'order_items':order_items , 'base_template': base_template 
        }) # passing order data


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'order/order_history.html', {'orders': orders, 'base_template': base_template})


@login_required
def order_list(request):
    orders = Order.objects.all()
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'order/order_list.html', {'orders':orders ,'base_template': base_template })
