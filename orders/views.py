#corrected code working well 

from django.shortcuts import render, redirect
from django.http import HttpResponse
from carts.models import Cart, CartItem
from . forms import OrderForm
from .models import Order, Payment, OrderProduct
import datetime
from store.models import Product
from django.contrib.auth.decorators import login_required
from accounts import views
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from accounts.models import Account
from django.views.decorators.cache import never_cache
# Create your views here.


@never_cache
@login_required(login_url='login')
def payments(request, order_number):
    
    #here we will get only the current user
    if request.method == 'GET':
        order = Order.objects.filter(
            user=request.user,
            is_ordered=False,
            order_number=order_number
        ).first()

        #this is the main check after order, go to dashboard
        if not order or order.is_ordered:
            return redirect('my_orders')

        cart_items = CartItem.objects.filter(user=request.user)

        total = sum(item.products.price * item.quantity for item in cart_items)
        tax = (2 * total) / 100
        grand_total = total + tax

        #pass the context in the payemnts

        return render(request, 'orders/payments.html', {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
        })

    # ---------- POST : static payment success ----------
    order_number = request.POST.get('order_number')
    if not order_number:
        return redirect('store')

    order = Order.objects.filter(
        user=request.user,
        is_ordered=False,
        order_number=order_number
    ).first()

    if not order:
        return redirect('store')

    payment_id = f"SIM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    payment = Payment(
        user=request.user,
        payment_id=payment_id,
        payment_method='Simulated',
        amount_paid=order.order_total,
        status='COMPLETED',
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # ---------- move cart items to order product ----------
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.products_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.products.price
        orderproduct.ordered = True
        orderproduct.save()

        orderproduct.variation.set(item.variations.all())

        product = Product.objects.get(id=item.products_id)
        product.stock = max(0, product.stock - item.quantity)
        product.save()

    # ---------- clear cart ----------
    CartItem.objects.filter(user=request.user).delete()

    # ---------- send confirmation email ----------
    mail_subject = 'Thank You for your purchase'
    message = render_to_string(
        'orders/order_received_email.html',
        {
            'user': request.user,
            'order': order,
        }
    )

    EmailMessage(mail_subject, message, to=[request.user.email]).send()

    return redirect('order_complete')






#func for placing an order

@login_required(login_url='login')
def place_order(request, total = 0, quantity=0):

    current_user = request.user

    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()

    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.products.price * cart_item.quantity )
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

     # if request.method=='GET':
    #     print("here")
    #     ord = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at').first()
    #     print(ord,ord.payment)
    #     if ord is not None and ord.payment is None:
    #         print( ord.payment)
    #         # print()
    #         return redirect('home')
    
    # if request.method == 'POST':
    #     ord = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at').first()
    #     print(ord,ord.payment)
    #     if ord is not None and ord.payment is None:
    #         print( ord.payment)
    #         # print()
    #         return redirect('home')
    #     current_user = request.user

    #     cart_items = CartItem.objects.filter(user=current_user)
    #     cart_count = cart_items.count()

    #     if cart_count <= 0:
    #         return redirect('store')

    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            #generate an order number

            current_date = datetime.date.today().strftime("%Y%m%d")

            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            # context = {

            #     'order':order,
            #     'cart_items':cart_items,
            #     'total': total,
            #     'tax':tax,
            #     'grand_total':grand_total,
            # }
            return redirect('payments', order_number=order_number)

        else:
            print(form.errors)
            return redirect('checkout')
        


@never_cache
@login_required(login_url='login')
def order_complete(request):
    order = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at').first()
    if not order:
        return redirect('store')

    order_products = OrderProduct.objects.filter(order=order)

    context = {
        'order': order,
        'order_products': order_products,
        'payment': order.payment,
        'subtotal': order.order_total - order.tax,
        'tax': order.tax,
        'grand_total': order.order_total,
    }
    return render(request, 'orders/order_complete.html', context)
    





        









