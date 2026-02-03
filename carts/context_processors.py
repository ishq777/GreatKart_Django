from .models import Cart, CartItem
from django.shortcuts import redirect, render
from django.urls import path
from .views import _cart_id


def counter(request):

    cart_count = 0

    if 'admin' in request.path:
        return{}
    
    else:
        try:
            # this will get the cart of current session
            cart = Cart.objects.filter(cart_id = _cart_id(request))

            if request.user.is_authenticated:
                cart_items = CartItem.objects.all().filter(user=request.user)
            else:

                 # get all cart items and :1 here means just take one item (slicing concept)
                cart_items =  CartItem.objects.all().filter(cart=cart[:1])

            # go through the cart and count products
            for cart_item in cart_items:
                cart_count += cart_item.quantity
       
        except Cart.DoesNotExist:
            cart_count = 0
    
    return dict(cart_count=cart_count)

