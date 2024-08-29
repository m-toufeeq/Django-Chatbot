from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', index, name='index'),  
    path('signup/', signup_view, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='ChabotFeature/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('start_chat/', start_chat, name='start_chat'),
     path('respond/<int:step_id>/<int:option_id>/', handle_response, name='handle_response'),
]
