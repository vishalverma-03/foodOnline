from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages,auth
from vendor.forms import VendorForm
from .utils import detectUser,send_email_verification
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor
from django.template.defaultfilters import slugify
from orders.models import Order



# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            password = form.cleaned_data['password']  # Hash the password
            user.set_password(password)
            user.save()
            
            #email verification
            mail_subject = 'Please activate your account'
            email_template = 'accounts/email/account_verification_email.html'
            send_email_verification(request,user,mail_subject,email_template)
            
            messages.success(request, "Congratulations! You are registered successfully")
            return redirect('registerUser')  # Replace with your success page URL
        else:
            print('Invalid field details') 
            print(form.errors)   
    else:
        form = UserForm()  # Create a blank form

    context = {
        'form': form,  # Pass the form to the context
    }
    return render(request, 'accounts/registerUser.html', context)


def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method == 'POST':
        form = UserForm(request.POST)
        v_form = VendorForm(request.POST, request.FILES)
        if form.is_valid() and v_form.is_valid():
            user = form.save(commit=False)
            user.role = User.CUSTOMER
            password = form.cleaned_data['password']  # Hash the password
            user.set_password(password)
            user.role = User.VENDOR
            user.save()
            vendor = v_form.save(commit=False)
            vendor.user = user
            vendor_name=v_form.cleaned_data['vendor_name'] +'-'+str(user.id)
            vendor.vendor_slug=slugify(vendor_name)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()

            # email-verification
            mail_subject = 'Please activate your account'
            email_template = 'accounts/email/account_verification_email.html'
            send_email_verification(request,user,mail_subject,email_template)
            messages.success(request, "Vendor registered successfully.")
            return redirect('registerVendor')  
        else:
            print(form.errors)
            print(v_form.errors)

    else:
        form = UserForm()
        v_form = VendorForm()

    context = {
        'form': form,
        'v_form': v_form,
    }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=User._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,User.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'congratulation! your acount is activated')
        return redirect('myAccount')
    
    else:
        messages.error(request,'invalid acitvation link')
        return redirect('myAccount')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    elif request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email,password=password)

        if user is not None:
            auth.login(request,user)
            messages.success(request,'you are logged in successfully')
            return redirect('myAccount')
        else:
            messages.error(request,'invalid login cradentials')
            return redirect('login')

    return render(request,'accounts/login.html')

def logout(request):
    auth.logout(request)
    messages.info(request,'you are logged out')
    return redirect('login')

@login_required(login_url='login')
def myAccount(request):
    user=request.user
    redirectUrl=detectUser(user)
    return redirect(redirectUrl)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):    
    orders=Order.objects.filter(user=request.user,is_ordered=True)
    recent_orders=Order.objects.filter(user=request.user,is_ordered=True)[:3]
    context={
        'recent_orders':recent_orders,
        'orders_count':orders.count(),
    }
    return render(request,'accounts/custDashboard.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):    
    vendor=Vendor.objects.get(user=request.user)
    context={
        "vendor":vendor,
    }
    return render(request,'accounts/vendorDashboard.html',context)

def forgotPassword(request):
    if request.method=='POST':
        email=request.POST['email']

        if User.objects.filter(email=email).exists():
            user=User.objects.get(email__exact=email)

            # sending verification link
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/email/password_reset_email.html'
            send_email_verification(request, user, mail_subject, email_template)

            messages.success(request,'reset link is send to your email')
            return redirect('login')
        
        else:
            messages.error(request,'invalid email')
            return redirect('forgotPassword')
    return render(request,'accounts/forgotPassword.html')

def forgotPassowrd_reset_Link(request,uidb64,token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired!')
        return redirect('myAccount')

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match!')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
