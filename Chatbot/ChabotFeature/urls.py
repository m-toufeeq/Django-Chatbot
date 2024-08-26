from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),  # Renders the index.html at the root URL
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='ChabotFeature/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
