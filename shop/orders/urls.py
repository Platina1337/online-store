from django.urls import path
from .views import *
from . import views


urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('my-orders/', UserOrderListView.as_view(), name='user_orders'),
]