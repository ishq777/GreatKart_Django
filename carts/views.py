from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product
from django.core.exceptions import ObjectDoesNotExist

# returns a unique cart id for current session , a user may not be logged in but still imp to identify their cart
def _cart_id(request):
    cart = request.session.session_key #ask browser for existing key
    if not cart:
        cart = request.session.create() #if there isn't one, create one
    return cart

#this part will handle the cart actions like 
# 1. adding a product to the cart, if cart dont exists we create one
# 2. if there is a product already increase the quantity#

def add_cart(request, product_id):

    color = request.GET['Color']
    size = request.GET['Size']

    return HttpResponse(color + ' ' + size)
    exit()

    products = Product.objects.get(id=product_id)
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist: #here we create the cart
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )

    cart.save()

    try: # here we check if the product exists in the cart or not
        cart_item = CartItem.objects.get(products=products, cart=cart)
        cart_item.quantity +=1 #increase the quantity if there
        cart_item.save()
    
    # if there isnt a product in cart, we create a cart and start with 1 quantity
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(

            products = products,
            quantity = 1,
            cart = cart,
        )

        cart_item.save()
    return redirect('cart')

# to reduce the cart items
def reduce_cart_items(request, product_id):

    cart = Cart.objects.get(cart_id= _cart_id(request))
    products = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(products=products, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    
    return redirect('cart')

# to remove the entire product
def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id= _cart_id(request))
    products = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(products=products, cart=cart)
    cart_item.delete()

    return redirect('cart')




def cart(request, total=0, quantity=0, cart_item=None):
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.products.price * cart_item.quantity)
            quantity += cart_item.quantity

        tax = (2 * total) / 100
        grand_total = tax + total
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total': grand_total,

    }

    return render(request, 'store/cart.html', context)
