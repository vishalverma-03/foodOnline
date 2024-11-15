let autocomplete;

function initAutoComplete(){
autocomplete = new google.maps.places.Autocomplete(
    document.getElementById('id_address'),
    {
        types: ['geocode', 'establishment'],
        //default in this app is "IN" - add your country code
        componentRestrictions: {'country': ['in']},
    })
// function to specify what should happen when the prediction is clicked
autocomplete.addListener('place_changed', onPlaceChanged);
}

function onPlaceChanged (){
    var place = autocomplete.getPlace();

    // User did not select the prediction. Reset the input field or alert()
    if (!place.geometry){
        document.getElementById('id_address').placeholder = "Start typing...";
    }
    else{
        console.log('place name=>', place.name)
    }
    // get the address components and assign them to the fields
}
$(document).ready(function(){
    $('.add_to_cart').on('click', function(e){
        e.preventDefault();

        let food_id = $(this).attr('data-id');
        let url = $(this).attr('data-url'); // Use the data-url attribute here  

        $.ajax({
            type: 'GET',
            url: url,  // Use the 'url' variable instead of 'url' 
            success: function(response){
                console.log(response);
                if(response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location='/login';
                    })
                }
                else if (response.status === 'Success') {
                    // Update the quantity or other elements on success if needed
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    totalCartAmount(response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']
                    )
                }
                else {
                    swal(response.message,'','error')
                }
            },
        });
    });
    $('.item_qty').each(function(){
        let the_id=$(this).attr('id')
        let qty=$(this).attr('data-qty')
        $('#'+the_id).html(qty)
    })

    // decrease the cart quantity
    $('.decrease_cart').on('click', function(e){
        e.preventDefault();

        let food_id = $(this).attr('data-id');
        let url = $(this).attr('data-url'); // Use the data-url attribute here
        let cart_id=$(this).attr('id');
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                if(response.status == 'login_required'){
                    swal(response.message,'','info').then(function(){
                        window.location='/login';
                    })
                }
                else if (response.status === 'Success') {  
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    $('#qty-'+food_id).html(response.qty);
                    if(window.location.pathname=='/cart/'){
                    removeCartItem(response.qty,cart_id);
                    checkEmptyCart();
                    totalCartAmount(response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']
                    )
                    }
                } 
                else {
                    swal(response.message,'','error')
                }
            },
        });
    })
    // delete cart
    $('.delete_cart').on('click', function(e){
        e.preventDefault();
        
        let cart_id = $(this).attr('data-id');
        let url = $(this).attr('data-url'); // Use the data-url attribute here

        $.ajax({
            type: 'GET',
            url: url,
            success: function(response){
                console.log(response)
                if(response.status === 'Failed'){
                    swal(response.message,'','error')
                }  
                else{  
                    $('#cart_counter').html(response.cart_counter['cart_count']);
                    swal(response.status,response.message,'success');
                    removeCartItem(0,cart_id);
                    checkEmptyCart();
                    totalCartAmount(response.cart_amount['subtotal'],
                        response.cart_amount['tax'],
                        response.cart_amount['grand_total']
                    )
                } 
            },
        });
    });
    // delete the cart element have zero quantity
    function removeCartItem(cartItemQty,cart_id){
       
          if(cartItemQty<=0){
              document.getElementById("cart-item-"+cart_id).remove()
           }
        
    }
    function checkEmptyCart(){
        let cart_counter=document.getElementById('cart_counter').innerHTML
        if(cart_counter==0){
            document.getElementById("empty-cart").style.display="block";
        }
    }
    function totalCartAmount(subtotal,tax,grand_total){
        if(window.location.pathname=='/cart/'){
            $('#subtotal').html(subtotal)
            $('#tax').html(tax)
            $('#total').html(grand_total)
        }
    }
})
