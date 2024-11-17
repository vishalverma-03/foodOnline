from .models import Cart,Tax
from menu.models import FoodItem

def get_cart_count(request):
    cart_count=0
    if request.user.is_authenticated:
        try:
            cart_items=Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count+=cart_item.quantity
            else:
                cart_count=0;        
        except:
            cart_count=0;    
    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    grand_total = 0
    tax_dict = {}

    # Ensure the user is authenticated
    if request.user.is_authenticated:
        # Fetch cart items for the user
        cart_items = Cart.objects.filter(user=request.user)

        # Calculate subtotal
        for item in cart_items:
            try:
                fooditem = FoodItem.objects.get(pk=item.fooditem.id)
                subtotal += fooditem.price * item.quantity
            except FoodItem.DoesNotExist:
                # Handle case where FoodItem doesn't exist
                continue

        # Fetch active taxes
        active_taxes = Tax.objects.filter(is_active=True)
        for tax_entry in active_taxes:
            tax_type = tax_entry.tax_type
            tax_percentage = tax_entry.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): tax_amount}})

        # Calculate total tax
        tax = sum(
            tax_amount
            for tax_details in tax_dict.values()
            for tax_amount in tax_details.values()
        )

        # Grand total calculation
        grand_total = subtotal + tax

        # Debugging output (optional, can be removed in production)
        print(f"Tax Breakdown: {tax_dict}")
        print(f"Subtotal: {subtotal}, Tax: {tax}, Grand Total: {grand_total}")

    # Return the calculated amounts
    return dict(
        subtotal=subtotal,
        tax=tax,
        grand_total=grand_total,
        tax_dict=tax_dict,
    )
