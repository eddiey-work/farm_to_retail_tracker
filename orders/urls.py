from django.urls import path
from . import views

urlpatterns = [
    path("my/", views.my_orders, name="my_orders"),
    path("received/", views.incoming_orders, name="incoming_orders"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/confirm/", views.order_confirm, name="order_confirm"),
    path("<int:pk>/complete/", views.order_complete, name="order_complete"),
    path("<int:pk>/cancel/", views.order_cancel, name="order_cancel"),
]
