document.addEventListener('DOMContentLoaded', function() {
    // Variables
    const cartItems = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    const cartCount = document.getElementById('cart-count');
    
    let cart = [];

    // Inicializar el carrito desde localStorage si existe
    if (localStorage.getItem('cart')) {
        cart = JSON.parse(localStorage.getItem('cart'));
        updateCartUI();
        updateCartCount();
    }

    // Agregar al carrito
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.id;
            const itemName = this.dataset.name;
            const itemPrice = parseFloat(this.dataset.price);

            const item = {
                id: itemId,
                name: itemName,
                price: itemPrice,
                quantity: 1
            };

            addToCart(item);
            updateCartUI();
            showToast('Producto agregado al carrito');
        });
    });

    // Función para agregar al carrito
    function addToCart(item) {
        const existingItem = cart.find(i => i.id === item.id);
        if (existingItem) {
            existingItem.quantity++;
        } else {
            cart.push({
                ...item,
                price: parseInt(item.price) // Asegurar que el precio sea un número
            });
        }
        updateCartCount();
        localStorage.setItem('cart', JSON.stringify(cart));
    }

    // Actualizar UI del carrito
    function updateCartUI() {
        if (!cartItems) return;
        
        cartItems.innerHTML = '';
        let total = 0;

        cart.forEach(item => {
            const itemTotal = parseInt(item.price) * parseInt(item.quantity);
            total += itemTotal;

            const itemElement = document.createElement('div');
            itemElement.className = 'cart-item d-flex justify-content-between align-items-center p-2 border-bottom';
            itemElement.innerHTML = `
                <div>
                    <h6 class="mb-0">${item.name}</h6>
                    <div class="d-flex align-items-center">
                        <button class="btn btn-sm btn-outline-secondary me-2 decrease-quantity" data-id="${item.id}">-</button>
                        <span class="quantity">${item.quantity}</span>
                        <button class="btn btn-sm btn-outline-secondary ms-2 increase-quantity" data-id="${item.id}">+</button>
                    </div>
                    <small class="text-muted">$${formatPrice(item.price)} x ${item.quantity} = $${formatPrice(itemTotal)}</small>
                </div>
                <div class="d-flex align-items-center">
                    <button class="btn btn-sm btn-outline-danger remove-item" data-id="${item.id}">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            cartItems.appendChild(itemElement);

            // Agregar event listeners para los botones
            const decreaseBtn = itemElement.querySelector('.decrease-quantity');
            const increaseBtn = itemElement.querySelector('.increase-quantity');
            const removeBtn = itemElement.querySelector('.remove-item');

            decreaseBtn.addEventListener('click', () => updateQuantity(item.id, -1));
            increaseBtn.addEventListener('click', () => updateQuantity(item.id, 1));
            removeBtn.addEventListener('click', () => removeItem(item.id));
        });

        if (cartTotal) {
            cartTotal.textContent = formatPrice(total);
        }
    }

    // Función para actualizar cantidad
    function updateQuantity(itemId, change) {
        const item = cart.find(i => i.id === itemId);
        if (item) {
            item.quantity += change;
            if (item.quantity <= 0) {
                removeItem(itemId);
            } else {
                localStorage.setItem('cart', JSON.stringify(cart));
                updateCartUI();
                updateCartCount();
            }
        }
    }

    // Función para eliminar item
    function removeItem(itemId) {
        cart = cart.filter(i => i.id !== itemId);
        localStorage.setItem('cart', JSON.stringify(cart));
        updateCartUI();
        updateCartCount();
    }

    // Actualizar contador del carrito
    function updateCartCount() {
        if (!cartCount) return;
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        cartCount.textContent = totalItems;
    }

    // Formatear precio
    function formatPrice(price) {
        return new Intl.NumberFormat('es-CL', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(price);
    }

    // Usar el sistema de toasts modernos
    function showToast(message, type = 'success') {
        if (window.Toast) {
            window.Toast[type](message);
        }
    }

    // Enviar pedido
    window.submitOrder = function() {
        if (cart.length === 0) {
            showToast('El carrito está vacío', 'warning');
            return;
        }

        // Obtener botón y agregar loading state
        const submitButton = document.querySelector('[onclick="submitOrder()"]');
        let originalState = null;
        if (submitButton && window.LoadingState) {
            originalState = window.LoadingState.start(submitButton, 'Enviando pedido...');
        }

        // Obtener el número de mesa de la URL si existe
        const pathParts = window.location.pathname.split('/');
        const token = pathParts[pathParts.length - 1];

        // Preparar los datos del pedido
        const orderData = {
            items: cart.map(item => ({
                id: item.id,
                quantity: item.quantity
            })),
            is_delivery: !token,
            table_number: null
        };

        fetch(CREATE_ORDER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(orderData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(data => {
            // Restaurar estado del botón
            if (submitButton && originalState && window.LoadingState) {
                window.LoadingState.stop(submitButton, originalState);
            }

            if (data.success) {
                showToast('Pedido enviado correctamente', 'success');
                cart = [];
                localStorage.removeItem('cart');
                updateCartUI();
                updateCartCount();
                // Cerrar el modal
                const cartModal = bootstrap.Modal.getInstance(document.getElementById('cartModal'));
                if (cartModal) {
                    cartModal.hide();
                }
            } else {
                showToast(data.error || 'Error al enviar el pedido', 'error');
            }
        })
        .catch(error => {
            // Restaurar estado del botón
            if (submitButton && originalState && window.LoadingState) {
                window.LoadingState.stop(submitButton, originalState);
            }

            console.error('Error:', error);
            showToast('Error al enviar el pedido', 'error');
        });
    };
});
