from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Renders the index.html at the root URL
]
