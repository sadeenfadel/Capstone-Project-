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
from django.utils import timezone
from datetime import timedelta
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
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    
    return render(request, 'buoquet/bouquet_details.html', {'detail': detail ,  'base_template': base_template} )

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

        # we get the orders with pending status means the user can add more bouquet to that order
        existing_order = Order.objects.filter(user=request.user, status='pending').first()
        if existing_order:
        # modifying the total_price 
           existing_order.total_price += bquet.total_price * qnt 
           existing_order.save()

           OrderBouquet.objects.create(order =existing_order , bouquet = bquet , quantity=qnt , bouquet_name = bquet.name)
           order = existing_order 
        else:
            order = Order.objects.create(
                user=request.user,
                total_price=bquet.total_price * qnt
            )

            OrderBouquet.objects.create(
                order=order,
                bouquet=bquet,
                quantity=qnt,
                bouquet_name=bquet.name
            )
        messages.success(request, f"Your order for {bquet.name} x{qnt} has been placed! 🌸")
        return redirect('order_dtail'  , pk = order.id)
    return render (request , 'order/create_order.html' , {'boq' : bquet}) # here we render the page passing to it the boq details 


@login_required
def order_details(request, pk):
    if request.user.is_superuser:  # making sure its admin
    
        order = get_object_or_404(Order, pk=pk)
    else:
        # user seeing ite orders
        order = get_object_or_404(Order, pk=pk, user=request.user)

    order_items = order.orderbouquet_set.all()  # all bouquets inside the order

    for item in order_items:
        item.subtotal = item.bouquet.total_price * item.quantity

    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'

    return render(
        request,
        'order/order_detail.html',
        {
            'order': order,
            'order_items': order_items,
            'base_template': base_template
        }
    )


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'order/order_history.html', {'orders': orders, 'base_template': base_template})


@login_required
def order_list(request):
    orders = Order.objects.all()
    for order in orders:
        order.items = order.orderbouquet_set.all()  # كل البوكيهات المرتبطة بالأوردر

    base_template = 'admin_base.html' if request.user.is_superuser else 'base.html'
    return render(request, 'order/order_list.html', {'orders':orders ,'base_template': base_template })


@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.status = 'ready'
        order.save()
        messages.success(request, f"Order #{order.id} marked as ready!")
    return redirect('order_list')


@login_required
def confirm_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == 'POST':
        order.status = 'confirmed'
        order.save()
        messages.success(request, "Order confirmed!")
    return redirect('order_history')

# def delete_unconfirmed_orders():     for future
#     threshold = timezone.now() - timedelta(hours=48)
#     orders_to_delete = Order.objects.filter(status='ready', order_date__lt=threshold)
#     orders_to_delete.delete()

@login_required
@user_passes_test(lambda u: u.is_superuser)
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != "confirmed":  
        order.delete()
        messages.success(request, f"Order #{pk} has been canceled.")
    else:
        messages.warning(request, "Cannot cancel an order that has been confirmed.")
    return redirect('order_list')


@login_required
def remove_bouquet_from_order(request, order_id, bouquet_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    OrderBouquet.objects.filter(order=order, bouquet_id=bouquet_id).delete()

   
    messages.success(request, "Bouquet removed from your order.")

    total = 0
    for item in order.orderbouquet_set.all():
        total += item.bouquet.total_price * item.quantity
    order.total_price = total
    order.save()

    return redirect('order_dtail', pk=order.id)


@login_required
def edit_bouquet_quantity(request, order_id, bouquet_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_item = get_object_or_404(OrderBouquet, order=order, bouquet_id=bouquet_id)

    if request.method == "POST":
        new_quantity = int(request.POST.get("quantity"))
        if new_quantity > 0:
            order_item.quantity = new_quantity
            order_item.save()

            # تحديث السعر الإجمالي للأوردر
            total = sum(
                item.bouquet.total_price * item.quantity
                for item in order.orderbouquet_set.all()
            )
            order.total_price = total
            order.save()

            messages.success(request, f"Quantity updated to {new_quantity}.")
        else:
            messages.warning(request, "Quantity must be greater than 0.")

        return redirect("order_dtail", pk=order.id)

    return render(request, "order/edit_quantity.html", {
        "order_item": order_item,
        "order": order
    })
