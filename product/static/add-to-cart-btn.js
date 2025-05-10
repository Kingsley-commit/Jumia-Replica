function updateCart(elem, updateCartBtnGroup, ldsFacebook){
    redirectToLogin()
    ldsFacebook.classList.add('show')
    let action = elem.getAttribute('data-action')
    let product_id = elem.getAttribute('data-productid')
    return fetch('../../update_cart/', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken':csrftoken
        },
        body: JSON.stringify({
        'action': action,
        'product_id': product_id
        }),
    })
    .then(response => response.json())
    }

    function incrementCartCount(elem){
        let action = elem.getAttribute('data-action')
        let cartCount = document.getElementById('cart-count')
        if(action=='increment'){
            cartCount.textContent = parseInt(cartCount.textContent) + 1 
        }else{
            cartCount.textContent = parseInt(cartCount.textContent) - 1 
        }
    }

document.querySelectorAll('.update-cart-cta.initial').forEach((elem)=> {
    elem.addEventListener('click', ()=>{
        redirectToLogin()
        elem.classList.add('hide')
        let updateCartBtnGroup = elem.parentElement.querySelector('.update-cart-btn-group')
        let ldsFacebook = elem.parentElement.querySelector('.lds-facebook')
        updateCart(elem, updateCartBtnGroup, ldsFacebook)
        .then(data => {
            console.log('Success:', data);
            ldsFacebook.classList.remove('show')
            updateCartBtnGroup.classList.add('show')
            updateCartBtnGroup.querySelector('.product-count').textContent = data['quantity']
            incrementCartCount(elem)
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    })
})

document.querySelectorAll('.update-cart-cta-child').forEach((elem) => {
    elem.addEventListener('click', () => {
        redirectToLogin()
        elem.parentElement.classList.remove('show')
        let updateCartBtnGroup = elem.parentElement
        let ldsFacebook = updateCartBtnGroup.parentElement.querySelector('.lds-facebook')
        updateCart(elem, updateCartBtnGroup, ldsFacebook)
        .then(data => {
            console.log('Success:', data);
            ldsFacebook.classList.remove('show')
            if(data['quantity'] == 0){
                updateCartBtnGroup.parentElement.querySelector('.update-cart-cta').classList.remove('hide')
            }else{
                updateCartBtnGroup.classList.add('show')
                updateCartBtnGroup.querySelector('.product-count').textContent = data['quantity']
            }
            incrementCartCount(elem)
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    })
})