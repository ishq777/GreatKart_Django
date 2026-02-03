from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.views import login

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
    product = Product.objects.get(id=product_id)
    current_user = request.user

    # --------------------------------------------------
    # STEP 1: Collect product variations from POST
    # --------------------------------------------------
    product_variation = []

    if request.method == "POST":
        for key, value in request.POST.items():
            try:
                variation = Variation.objects.get(
                    product=product,
                    variation_category__iexact=key,
                    variation_value__iexact=value
                )
                product_variation.append(variation)
            except:
                pass

    # --------------------------------------------------
    # STEP 2: Decide cart owner (USER or SESSION CART)
    # --------------------------------------------------
    cart = None
    if not current_user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # --------------------------------------------------
    # STEP 3: Fetch cart items for this product & owner
    # --------------------------------------------------
    if current_user.is_authenticated:
        cart_items = CartItem.objects.filter(
            products=product,
            user=current_user
        )
    else:
        cart_items = CartItem.objects.filter(
            products=product,
            cart=cart
        )

    # --------------------------------------------------
    # STEP 4: Match variations
    # --------------------------------------------------
    ex_var_list = []
    item_ids = []

    for item in cart_items:
        ex_var_list.append(list(item.variations.all()))
        item_ids.append(item.id)

    # --------------------------------------------------
    # STEP 5: Increase quantity OR create new cart item
    # --------------------------------------------------
    if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item = CartItem.objects.get(id=item_ids[index])
        item.quantity += 1
        item.save()
    else:
        cart_item = CartItem.objects.create(
            products=product,
            quantity=1,
            user=current_user if current_user.is_authenticated else None,
            cart=None if current_user.is_authenticated else cart
        )
        if product_variation:
            cart_item.variations.add(*product_variation)
        cart_item.save()

    return redirect('cart')





# to reduce the cart items
def reduce_cart_items(request, product_id, cart_item_id):
    products = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(id=cart_item_id, user=request.user, products=products)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart, products=products)
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart')


# to remove the entire product
def remove_cart_item(request, product_id,cart_item_id):
    products = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        CartItem.objects.filter(products=products, user=request.user, id=cart_item_id).delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.filter(products=products, cart=cart, id=cart_item_id).delete()

    return redirect('cart')




def cart(request, total=0, quantity=0, cart_items=None):
    
    try:
        tax = 0
        grand_total = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
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


@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_item=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
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

    return render(request, 'store/checkout.html', context )
