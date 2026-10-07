from django.urls import path
from . import views

urlpatterns = [
    path('', views.crop_list, name='marketplace'),
    path('crop/<int:pk>/', views.crop_detail, name='crop_detail'),
]