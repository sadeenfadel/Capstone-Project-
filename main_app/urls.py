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
     path('bouquets/', views. bouquet_list, name='bouquet_list'),
      path('details/<int:pk>/', views. bouquet_details, name='bouquet_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)