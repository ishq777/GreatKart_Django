from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account, MyAccountManager
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.http import HttpResponse

#verification mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator


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
    if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = auth.authenticate(username=email,password=password)

            if user is not None:
                 auth.login(request,user)
                #  messages.success(request, 'u r logged in')
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
     return render(request, 'accounts/dashboard.html')



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
     