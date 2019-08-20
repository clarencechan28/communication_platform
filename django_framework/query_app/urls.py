from django.urls import path

from . import views

# Add more paths and functions in views in order to add different functionality with parameters
urlpatterns = [
    path('<str:bool>/', views.index),
]