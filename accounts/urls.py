from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.myAccount,name='account'),
    path('registerUser/', views.registerUser,name='registerUser'),
    path('registerVendor/', views.registerVendor,name='registerVendor'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('myAccount/',views.myAccount,name='myAccount'),
    path('custDashboard/',views.custDashboard,name='custDashboard'),
    path('vendorDashboard/',views.vendorDashboard,name='vendorDashboard'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('forgotPassword/',views.forgotPassword,name='forgotPassword'),
    path('forgotPassword_reset_Link/<uidb64>/<token>',views.forgotPassowrd_reset_Link,name='forgotPassword_reset_Link'),
    path('resetPassword/',views.resetPassword,name='resetPassword'),
    path('vendor/', include('vendor.urls')),
    path('customer/', include('customers.urls')),
]