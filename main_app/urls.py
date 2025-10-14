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
     path ('bouquet/<int:pk>/order/' , views.create_order , name = 'create_order'),
     path ('bouquet/<int:pk>/detail/' , views. order_details , name = 'order_dtail'),   # No Order matches the given query.  // The current path, bouquet/17/detail/, 17 is bouquet id not order id
     #path('order/<int:pk>/', views.order_details, name='order_dtail'),
     path('order/<int:pk>/update_status/', views.update_order_status, name='update_order_status'),
     path('order/<int:pk>/confirm/', views.confirm_order, name='confirm_order'),
     path('order/<int:order_id>/remove/<int:bouquet_id>/', views.remove_bouquet_from_order , name= 'deleteboq'),

     path('history/', views.order_history , name='order_history'),
     path('oderlist/', views.order_list , name='order_list'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)