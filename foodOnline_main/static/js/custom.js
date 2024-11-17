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
                // console.log(response);
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
                        response.cart_amount['tax_dict'],
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
                        response.cart_amount['tax_dict'],
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
                // console.log(response)
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
    function totalCartAmount(subtotal,tax_dict,grand_total){
        if(window.location.pathname=='/cart/'){
            $('#subtotal').html(subtotal)
            $('#total').html(grand_total)
            for( key1 in tax_dict){
                for(key2 in tax_dict[key1]){
                    console.log(tax_dict[key1][key2])
                    $(`#tax-${key1}`).html(tax_dict[key1][key2])
                }
            }
        }
    }

    // opening  hour add
    $('.add_hour').on('click', function (e) {
        e.preventDefault();
        let day = document.getElementById('id_day').value;
        let from_hour = document.getElementById('id_from_hour').value;
        let to_hour = document.getElementById('id_to_hour').value;
        let is_closed = document.getElementById('id_is_closed').checked;
        let csrf_token = $('input[name=csrfmiddlewaretoken]').val();
        let url = document.getElementById('add_hour_url').value;
    
        console.log(day, from_hour, to_hour, is_closed, csrf_token);
    
        // Validate inputs
        if ((is_closed && day !== '') || (!is_closed && day !== '' && from_hour !== '' && to_hour !== '')) {
            $.ajax({
                type: 'POST',
                url: url,
                data: {
                    'day': day,
                    'from_hour': from_hour,
                    'to_hour': to_hour,
                    'is_closed': is_closed ? 'True' : 'False',
                    'csrfmiddlewaretoken': csrf_token,
                },
                success: function (response) {
                    if (response.status === 'success') {
                        let html = '';
                        if (response.is_closed === 'Closed') {
                            html = `
                                <tr id=hour-${response.id}>
                                    <td style="border: none;"><b>${response.day}</b></td>
                                    <td style="border: none;">Closed</td>
                                    <td style="border: none;">
                                        <a href="#" class='remove_hour' data-url='vendor/opening-hour/remove/${response.id}'>Remove</a>
                                    </td>
                                </tr>`;
                        }
                        else{
                            html = `
                                <tr id=hour-${response.id}>
                                    <td style="border: none;"><b>${response.day}</b></td>
                                    <td style="border: none;">${response.from_hour} - ${response.to_hour}</td>
                                    <td style="border: none;">
                                        <a href="#" class='remove_hour' data-url='remove/${response.id}'>Remove</a>
                                    </td>
                                </tr>`;
                            }
                        $(".tbody_opening_hour").append(html);
                        document.getElementById("opening_hour").reset();
                    } 
                    else {
                        swal(response.message, '', "error");
                    }
                },
            });
        } else {
            swal('Please fill all the fields', '', 'info');
        }
    });

    // remove opening hour
    $(document).on('click', '.remove_hour', function(e) {
        e.preventDefault();
        url = $(this).attr('data-url');
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                if (response.status === 'success') {
                    console.log(url)
                    document.getElementById(`hour-${response.id}`).remove();
                    console.log(response);
                } 
            }
        });
    });       
})
