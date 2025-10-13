from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     path('', views.home, name='home'),
     path('about/', views.about, name='about'),
     path('contact/', views.contact, name='contact'),
     path('signup/', views.signup_view, name='signup'),
     path('login/', views.login_view, name='login'),
     path('logout/', views.logout_view, name='logout'),
     path('bouquets/', views.bouquet_list, name='bouquet_list'),
     path('details/<int:pk>/', views.bouquet_details, name='bouquet_detail'),
     path('profile/', views.profile_view, name='profile'),
     path('profile/edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
     path('profile/delete_account/', views.ProfileDeleteView.as_view(), name='delete_account'),
     path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
     path('create/', views.create_bouquet, name='create_bouquet'),
     path('bouquet/<int:pk>/edit/', views.edit_bouquet, name='edit_bouquet'),
    path('bouquet/<int:pk>/delete/', views.delete_bouquet, name='delete_bouquet'),
     # # path('admin/orders/', views.admin_orders, name='admin_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)