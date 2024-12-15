from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse,JsonResponse
from vendor.models import Vendor
from menu.models import Category,FoodItem
from django.db.models import Prefetch
from .models import Cart
from vendor.models import OpeningHour
from .context_processors import get_cart_count,get_cart_amounts
from datetime import date,datetime
from orders.forms import OrderForm
from accounts.models import UserProfile
from django.contrib.auth.decorators import login_required

# Create your views here.

def marketplace(request):
    vendors=Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count=vendors.count()
    context={
        'vendors':vendors,
        'vendor_count':vendor_count
    }
    return render(request,'marketplace/listing.html',context)

def vendor_detail(request,vendor_slug):
    vendor=get_object_or_404(Vendor,vendor_slug=vendor_slug)
    categories=Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset=FoodItem.objects.filter(is_available=True)
        )
    )

    opening_hour=OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
     
    today_date=date.today()
    today=today_date.isoweekday()
    current_day_opening_hour=OpeningHour.objects.filter(vendor=vendor, day=today)

    if request.user.is_authenticated:
        cart_items=Cart.objects.filter(user=request.user)
    else:
        cart_items=None    
    context={
        'vendor':vendor,  
        'categories':categories,
        'cart_items':cart_items,
        'opening_hour':opening_hour,
        'current_day_opening_hour':current_day_opening_hour,
    }
    return render(request,'marketplace/vendor_detail.html',context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                
                # Check if the cart item already exists
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    check_cart.quantity += 1
                    check_cart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Food item quantity updated in cart', 'cart_counter': get_cart_count(request),'qty':check_cart.quantity,'cart_amount':get_cart_amounts(request)})
                
                except:
                    # Create a new cart item if it doesn't exist
                    Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Food item added to cart','cart_counter': get_cart_count(request) ,'qty':1,'cart_amount':get_cart_amounts(request)})
            
            except FoodItem.DoesNotExist:
                return JsonResponse({'status': 'Failed', 'message': 'Food item does not exist'}, status=404)
        
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request type'}, status=400)
    
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    
def decrease_cart(request,food_id):   
    if request.user.is_authenticated:
        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                
                # Check if the cart item already exists
                try:
                    check_cart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    if check_cart.quantity>0:
                       check_cart.quantity -= 1
                       check_cart.save()
                    else:
                      check_cart.delete()
                      check_cart.quantity=0
                    return JsonResponse({'status': 'Success', 'message': 'Food item quantity updated in cart', 'cart_counter': get_cart_count(request),'qty':check_cart.quantity ,'cart_amount':get_cart_amounts(request)})
                
                except:
                    # Create a new cart item if it doesn't exist
                    return JsonResponse({'status': 'Failed', 'message': 'Food item is not added in cart'})
            
            except:
                return JsonResponse({'status':'Failed','message':'Food item does not exist'}, status=404)
        
        else:
            return JsonResponse({'status':'Failed','message':'Invalid request type'}, status=400)
    
    else:
        return JsonResponse({'status':'login_required','message':'Please login to continue'})
    
def cart(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    context={
        'cart_items':cart_items,
    }
    return render(request,'marketplace/cart.html',context)


def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                 cart_item=Cart.objects.get(user=request.user, id=cart_id)
                 if cart_item:
                     cart_item.delete()
                     return JsonResponse({'status':'Success','message':'Cart item has been deleted','cart_counter':get_cart_count(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status':'Failed','message':'Cart item does not exist'}) 
            
        else:
             return JsonResponse({'status':'Faied','message':'Invalid request'})
        
                   
@login_required(login_url='login')
def checkout(request):
    cart_items=Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count=cart_items.count()
    user_profile=UserProfile.objects.get(user=request.user)
    default_values={
        'first_name':request.user.first_name,
        'last_name':request.user.last_name,
        'phone':request.user.phone_number,
        'email':request.user.email,
        'address': user_profile.address if user_profile else '',
        'city': user_profile.city if user_profile else '',
        'state': user_profile.state if user_profile else '',
        'pin_code': user_profile.pin_code if user_profile else '',
        'country': user_profile.country if user_profile else '',

    }
    form=OrderForm(initial=default_values)
    if cart_count<=0:
        return redirect('marketplace')
    context={
        'form':form,
        'cart_items':cart_items
    }
    return render(request,'marketplace/checkout.html',context)                   