from django.shortcuts import render, redirect
from .forms import RegistrationForm, UserProfileForm, UserForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.http import HttpResponse
from carts.models import Cart, CartItem
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from orders.models import Order, OrderProduct
from django.shortcuts import get_object_or_404



# this is based on the models we r taking cleaned data
def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            username = email.split("@")[0] #this is how we can get a unique username

            user = Account.objects.create_user(first_name=first_name, last_name=last_name,email=email,username=username, password=password)
            user.phone_number = phone_number

            user.save()

            #this will crrate the userprofile default
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()


            #for user activation mail
            current_site = get_current_site(request)
            mail_subject = 'please activate ur account'
            message = render_to_string('accounts/account_verification_email.html',{
                 
                 'user':user,
                 'domain':current_site,
                 'uid':urlsafe_base64_encode(force_bytes(user.pk)), #this encodes the user id 
                 'token': default_token_generator.make_token(user), #and then a token is generated next to the user id
                 
                 })


            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            messages.success(request,'Thank You for registring with us, Pls confirm the verification mail to continue')
            return redirect('/accounts/login/?command=verification&email='+ email)


    else:
        form = RegistrationForm()
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html', context)



def login(request):
    from carts.views import _cart_id
    if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(username=email,password=password)
            
            if user is not None:
                   try:
                        cart = Cart.objects.get(cart_id=_cart_id(request))  
                        is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                        if is_cart_item_exists:
                             cart_items = CartItem.objects.filter(cart=cart)
                             for cart_item in cart_items:
                                   session_variations = list(cart_item.variations.all())

                                   user_items = CartItem.objects.filter(
                                        products=cart_item.products,
                                        user=user
                                   )

                                   matched = False

                                   for user_item in user_items:
                                        if list(user_item.variations.all()) == session_variations:
                                             user_item.quantity += cart_item.quantity
                                             user_item.save()
                                             matched = True
                                             break

                                   if not matched:
                                        cart_item.user = user
                                        cart_item.cart = None
                                        cart_item.save()
                                   else:
                                        cart_item.delete()
          
                   except:
                        pass
                        
                   auth.login(request,user) 
                   return redirect('home')

            else:  
              messages.error(request, 'invalid credentials')
              return redirect('login')
            
    return render(request, 'accounts/login.html')
    



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'u r logged out')
    return redirect('login')
# return render(request, 'accounts/logout.html')




def activate(request,uidb64, token):
    try:
          uid = urlsafe_base64_decode(uidb64).decode() #this will decode the base64 to a readable user id
          user = Account._default_manager.get(pk=uid) #user is identified through the user id itself
    except (TypeError,ValueError,OverflowError,Account.DoesNotExist):
         user = None

    if user is not None and default_token_generator.check_token(user, token): #this ensures the token is active and not expired
         user.is_active = True
         user.save()
         messages.success(request, 'Congratulations! Your account is activated')
         return redirect('login')
    
    else:
         messages.error(request, 'Invalid activation link')
         return redirect('register')
    
    
@login_required(login_url='login')
def dashboard(request):
     orders = Order.objects.order_by('created_at').filter(user_id=request.user.id, is_ordered=True)
     orders_count = orders.count()
     context = {

          'orders_count':orders_count,
     }
     return render(request, 'accounts/dashboard.html', context)



def ForgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) #if i say iexact it will become case sensitive
            
            #this is for user password reset
            current_site = get_current_site(request)
            mail_subject = 'please reset ur account password'
            message = render_to_string('accounts/reset_password_email.html',{
                 
                 'user':user,
                 'domain':current_site,
                 'uid':urlsafe_base64_encode(force_bytes(user.pk)), #this encodes the user id 
                 'token': default_token_generator.make_token(user), #and then a token is generated next to the user id
                 
                 })


            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request, 'Pls check your mail for password change')
            return redirect ('login')
           
        else:
            messages.error(request, 'Account with such email does not exist ')
            return redirect('register')
    
    return render(request, 'accounts/ForgotPassword.html')


def resetpassword_validate(request, uidb64, token):
    try:
         uid = urlsafe_base64_decode(uidb64).decode()
         user = Account._default_manager.get(pk=uid)
    except (TypeError, OverflowError, ValueError, Account.DoesNotExist):
         user = None

    if user is not None and default_token_generator.check_token(user, token):
         request.session['uid'] = uid
         messages.success(request, 'please reset your password')
         return redirect('resetPassword')
    
    else:
         messages.error(request, 'Link has been expired')
         return redirect('login')
    


        
def resetPassword(request):
     if request.method == 'POST':
          password = request.POST['password']
          confirm_password = request.POST['confirm_password']

          if password == confirm_password:
               uid = request.session.get('uid')
               user = Account.objects.get(pk=uid)
               user.set_password(password)
               user.save()
               messages.success(request, 'Your password has been reset')
               return redirect('login')
          
          else:
               messages.error(request, "pls check password") 
               return redirect('resetPassword')
     else:
          return render(request, 'accounts/resetPassword.html')
     

     
@login_required(login_url='login')
def my_orders(request):
     orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
     context = {
          'orders':orders,
     }
     return render(request, 'accounts/my_orders.html', context)





@login_required(login_url='login')
def edit_profile(request):
     userprofile = get_object_or_404(UserProfile, user=request.user)
     if request.method == 'POST':
          user_form = UserForm(request.POST, instance=request.user)
          profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
          if user_form.is_valid() and profile_form.is_valid():
               user_form.save()
               profile_form.save()
               messages.success(request, 'Your profile has been updated')
               return redirect('edit_profile')
     else:
          user_form = UserForm(instance=request.user)
          profile_form = UserProfileForm(instance=userprofile)

     context = {
          'user_form': user_form,
          'profile_form': profile_form,
          'userprofile':userprofile,
     }
     return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):

     if request.method == 'POST':

          current_password = request.POST['current_password']
          new_password = request.POST['new_password']
          confirm_password = request.POST['confirm_password']

          #user = Account.objects.get(user=request.user)
          user = Account.objects.get(username__exact=request.user.username) 

          if new_password == current_password:
               success = user.check_password(current_password)
               if success:
                    user.set_password(new_password)
                    user.save()

                    #auth.logout if u want to make the user logout 

                    messages.success(request, 'Password saved successfully')
                    return redirect('login')
               else:
                    messages.error(request, 'pls enter valid credentials')
                    return redirect('change_password')
               
          else:
               messages.error(request, "Passwords dont match")
               return redirect('change_password')


     return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):

     order_detail = OrderProduct.objects.filter(order__order_number=order_id) #refer from Order.models, order and then order_number
     order = Order.objects.get(order_number=order_id)
     subtotal = 0
     tax = 0
     for i in order_detail:
          subtotal += i.product_price * i.quantity

     tax = (2* subtotal) / 100

     grand_total = subtotal + tax
     


     context = {

          'order_detail':order_detail,
          'order':order,
          'subtotal': subtotal,
          'tax': tax,
          'grand_total' : grand_total,
     }


     return render(request,'accounts/order_detail.html', context)
