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
# Create your views here.



@login_required(login_url='login')
def payments(request):
    if request.method != 'POST':
        return redirect('store')

    order_number = request.POST.get('order_number')
    if not order_number:
        return redirect('store')
    order = Order.objects.filter(user=request.user, is_ordered=False, order_number=order_number).first()
    payment_id = f"SIM-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    payment = Payment(

        user = request.user,
        payment_id = payment_id,
        payment_method = 'Simulated',
        amount_paid = order.order_total,
        status = 'COMPLETED',
    )

    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    #move cart items to order product table

    cart_items = CartItem.objects.filter(user=request.user)
    cart_items_list = list(cart_items)

    for item in cart_items_list:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id 
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.products_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.products.price
        orderproduct.ordered = True
        orderproduct.save()

        product_variation = item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()

        #reduce item quantity in the cart

        product = Product.objects.get(id=item.products_id)
        product.stock = max(0, product.stock - item.quantity)
        product.save()


    #CLEAR CART
    CartItem.objects.filter(user=request.user).delete()


    #send mail to confirm

    # user = request.user
    mail_subject = 'Thank You for your purchase'
    message = render_to_string('orders/order_received_email.html',{
            
            'user': request.user,
            'order':order,
            })


    to_email = request.user.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()




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

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            context = {

                'order':order,
                'cart_items':cart_items,
                'total': total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return render(request, 'orders/payments.html', context)
        else:
            print(form.errors)
            return redirect('checkout')
        



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
    





        










