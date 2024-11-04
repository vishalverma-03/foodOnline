from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserForm
from .models import User, UserProfile
from django.contrib import messages,auth
from vendor.form import VendorForm
from .utils import detectUser
from django.contrib.auth.decorators import login_required,user_passes_test
from django.core.exceptions import PermissionDenied

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
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            
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
    return render(request,'accounts/custDashboard.html')

@user_passes_test(check_role_vendor)
def vendorDashboard(request):    
    return render(request,'accounts/vendorDashboard.html')