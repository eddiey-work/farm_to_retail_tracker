from django.urls import path
from . import views

urlpatterns = [
    path('crops/', views.my_crops, name='my_crops'),
    # Days 10-11 will add:
    path('crops/add/', views.crop_create, name='crop_create'),
    # path('crops/<int:pk>/edit/', views.crop_update, name='crop_update'),
    # path('crops/<int:pk>/delete/', views.crop_delete, name='crop_delete'),
]