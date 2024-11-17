from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse,HttpResponse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required,user_passes_test
from django.template.defaultfilters import slugify
from accounts.models import UserProfile
from django.contrib import messages
from .models import Vendor,OpeningHour
from .forms import VendorForm,OpeningHourForm
from accounts.forms import UserProfileForm
from accounts.views import check_role_vendor
from menu.models import Category,FoodItem
from menu.forms import CategoryForm,FoodItemForm
# Create your views here.

def get_vendor(request):
    vendor=Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form=UserProfileForm(instance=profile)
        vendor_form=VendorForm(instance=vendor)

    context={
        "profile_form":profile_form,
        "vendor_form":vendor_form,
        "profile":profile,
        "vendor":vendor,
    }
    return render(request,'vendor/vprofile.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor=get_vendor(request)
    categories=Category.objects.filter(vendor=vendor).order_by('created_at')
    context={
        'categories':categories
    }
    return render(request,'vendor/menu_builder.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def fooditems_by_category(request,pk=None):
    vendor=get_vendor(request)
    category=get_object_or_404(Category,pk=pk)
    fooditems=FoodItem.objects.filter(vendor=vendor,category=category)
    print(fooditems)
    context={
        'category':category,
        'fooditems':fooditems
    }
    return render(request,'vendor/fooditems_by_category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_name = category_form.cleaned_data['category_name']
            category = category_form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(category_form.errors)

    else:
        category_form = CategoryForm()
    context = {
        'category_form': category_form,
    }
    return render(request, 'vendor/add_category.html', context) 

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    # Get the category object by primary key
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        # Bind the form to the category instance
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)  # Set the vendor
            category.slug = slugify(category_name)
            category.save()
            messages.success(request, 'Category updated successfully')
            return redirect('menu_builder')  # Redirect to the menu builder page
        else:
            print(form.errors)
    else:
        # Initialize the form with the existing category instance
        form = CategoryForm(instance=category)

    context = {
        'form': form,
        'category': category
    }

    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request,pk=None):
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    messages.success(request,'Category deleted successfully')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            slug = slugify(food_title)
            vendor = get_vendor(request)
            if FoodItem.objects.filter(slug=slug, vendor=vendor).exists():
                form.add_error('food_title', 'A food item with this name already exists.')
            else:
                food = form.save(commit=False)
                food.vendor = vendor
                food.slug = slug  # Assign the generated slug
                food.save()
                messages.success(request, 'Food item created successfully')
                return redirect('fooditems_by_category', food.category.id)

        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))
    context = {
        'form': form
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request,pk=None):
    food=get_object_or_404(FoodItem,pk=pk)
    if request.method == 'POST':
        # Bind the form to the category instance
        form = FoodItemForm(request.POST,request.FILES,instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = get_vendor(request)  # Set the vendor
            food.slug = slugify(food_title)
            food.save()
            messages.success(request, 'food updated successfully')
            return redirect('fooditems_by_category',food.category.id)  # Redirect to the menu builder page
        else:
            print(form.errors)

    else:
        form=FoodItemForm(instance=food)
        form.fields['category'].queryset=Category.objects.filter(vendor=get_vendor(request))

    context={
        'form':form,
        'food':food
    }
    return render(request,'vendor/edit_food.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request,pk=None):
    food_item=get_object_or_404(FoodItem,pk=pk)
    food_item.delete()
    messages.success(request,'food delete successfully')
    return redirect('fooditems_by_category',food_item.category.id)

def opening_hour(request):
    opening_hour=OpeningHour.objects.filter(vendor=get_vendor(request))
    form=OpeningHourForm()
    context={
        'form':form,
        'opening_hour':opening_hour
    }
    return render(request,'vendor/opening_hour.html',context)

def add_opening_hour(request):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method=='POST':
            day=request.POST.get('day')
            from_hour=request.POST.get('from_hour')
            to_hour=request.POST.get('to_hour')
            is_closed=request.POST.get('is_closed')
            print(day,from_hour,to_hour,is_closed)
            try:
                hour=OpeningHour.objects.create(vendor=get_vendor(request),day=day,from_hour=from_hour,to_hour=to_hour,is_closed=is_closed)
                if hour:
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)   
        else:
            HttpResponse('invalid request')


    return HttpResponse('add opening hour')

def remove_opening_hour(request,pk=None):
    if request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          try:
              hour=get_object_or_404(OpeningHour,pk=pk)
              hour.delete()
              return JsonResponse({'status':'success','id':pk})
          
          except:
              return JsonResponse({'status':'failed','message':'invalid request','id':pk})