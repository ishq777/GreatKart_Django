from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Cart, CartItem
from store.models import Product, Variation
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
    products = Product.objects.get(id=product_id)
    product_variation = []
    
    if request.method == "POST":
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            try:
                variation = Variation.objects.get(product=products,variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
                print(variation)
            except:
                pass

    
    try:
        cart = Cart.objects.get(cart_id = _cart_id(request))
    except Cart.DoesNotExist: #here we create the cart
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )

    # cart.save()

    is_cart_item_exists = CartItem.objects.filter(products=products,cart=cart).exists()

    if is_cart_item_exists: # here we check if the product exists in the cart or not
        cart_item = CartItem.objects.filter(products=products, cart=cart)
        # existing variations and current variation
        # we need item_id

        #if current variation is already in the exisitng variations, then we increase the quantity

        ex_var_list = [] # this stores variations of the exisiting cart items

        id = [] #this gets the corresponsing cart item id

        for item in cart_item:
            existing_variation = item.variations.all()
            ex_var_list.append(list(existing_variation)) #frm here we taking the cart id as a list for comparison
            id.append(item.id) #also keep the item id 

        print(ex_var_list)
        

        #if the selected variotion exists in the cart, increase the count
        if product_variation in ex_var_list:
            # here we increase the quantity
            index = ex_var_list.index(product_variation) #index to match the same id for variation
            item_id = id[index]  #index to match the same id for item
            item = CartItem.objects.get(products=products, id=item_id)
            item.quantity += 1 #then we increase the quantity
            item.save()
           
           #this is if the variation is new
        else:
            item = CartItem.objects.create(products=products, quantity=1, cart=cart)

            if len(product_variation) > 0:
                item.variations.clear() 
                item.variations.add(*product_variation)
            item.save()
    
    # if there isnt a product in cart, we create a cart and start with 1 quantity
    else:
        cart_item = CartItem.objects.create(

            products = products,
            quantity = 1,
            cart = cart,
        )
        if len(product_variation) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation)
        cart_item.save()
    return redirect('cart')

# to reduce the cart items
def reduce_cart_items(request, product_id, cart_item_id):

    cart = Cart.objects.get(cart_id= _cart_id(request))
    products = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(id=cart_item_id)
    if cart_item:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    
    return redirect('cart')

# to remove the entire product
def remove_cart_item(request, product_id,cart_item_id):
    cart = Cart.objects.get(cart_id= _cart_id(request))
    products = get_object_or_404(Product, id=product_id)
    CartItem.objects.filter(products=products, cart=cart, id=cart_item_id).delete()

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
