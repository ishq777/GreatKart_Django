from django.urls import path
from . import views
from .models import Cart, CartItem

urlpatterns = [

    path('',views.cart, name='cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),#<int will dynamically mapp to product_id
    path('reduce_cart_items/<int:product_id>/<int:cart_item_id>/', views.reduce_cart_items, name='reduce_cart_items'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
]