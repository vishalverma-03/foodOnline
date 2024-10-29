from django.shortcuts import render,redirect
from django.http import HttpResponse,response
from .forms import UserForm
from .models import User
from django.contrib import messages
# Create your views here.

def registerUser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role=User.CUSTOMER
            password =(form.cleaned_data['password'])  # Hash the password
            user.set_password(password)
            user.save()
            messages.success(request,"Congratulations!  You are registered successfully")
            return redirect('registerUser')  # Replace with your success page URL
        else:
            print('invalid field details') 
            print(form.errors)   
    else:
        form = UserForm()  # Create a blank form

    context = {
        'form': form,  # Pass the form to the context
    }
    return render(request,'accounts/registerUser.html',context)
