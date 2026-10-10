from django.urls import path
from . import views

urlpatterns = [
    path("", views.crop_list, name="marketplace"),
    path("crop/<int:pk>/", views.crop_detail, name="crop_detail"),
    path("crop/<int:pk>/order/", views.place_order, name="place_order"),
    path(
        "orders/<int:pk>/confirmation/",
        views.order_confirmation,
        name="order_confirmation",
    ),
]
