// CartManager - Single source of truth for cart state using localStorage
const CartManager = {
    STORAGE_KEY: 'restqr_cart',
    
    // Validate cart data structure
    _validateCartData(data) {
        if (!Array.isArray(data)) {
            return false;
        }
        
        return data.every(item => {
            return item &&
                   typeof item === 'object' &&
                   (typeof item.id === 'string' || typeof item.id === 'number') &&
                   typeof item.name === 'string' &&
                   typeof item.price === 'number' &&
                   typeof item.quantity === 'number' &&
                   item.quantity > 0;
        });
    },
    
    // Get cart from localStorage
    getCart() {
        try {
            const cartData = localStorage.getItem(this.STORAGE_KEY);
            if (!cartData) {
                return [];
            }
            
            const parsed = JSON.parse(cartData);
            
            // Validate data structure
            if (!this._validateCartData(parsed)) {
                console.warn('Invalid cart data found in localStorage, resetting cart');
                localStorage.removeItem(this.STORAGE_KEY);
                return [];
            }
            
            return parsed;
        } catch (error) {
            console.error('Error reading cart from localStorage:', error);
            localStorage.removeItem(this.STORAGE_KEY);
            return [];
        }
    },
    
    // Save cart to localStorage
    saveCart(cart) {
        try {
            // Validate before saving
            if (!this._validateCartData(cart)) {
                console.error('Attempted to save invalid cart data');
                return false;
            }
            
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(cart));
            this.updateDisplay();
            return true;
        } catch (error) {
            console.error('Error saving cart to localStorage:', error);
            return false;
        }
    },
    
    // Add item to cart
    addItem(itemId, name, price, quantity = 1) {
        const cart = this.getCart();
        const existingItem = cart.find(item => item.id == itemId);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            cart.push({
                id: itemId,
                name: name,
                price: parseFloat(price),
                quantity: quantity
            });
        }
        
        this.saveCart(cart);
        this._showToast('Producto agregado al carrito');
    },
    
    // Remove item from cart
    removeItem(itemId) {
        let cart = this.getCart();
        cart = cart.filter(item => item.id != itemId);
        this.saveCart(cart);
    },
    
    // Update quantity
    updateQuantity(itemId, quantity) {
        const cart = this.getCart();
        const item = cart.find(item => item.id == itemId);
        
        if (item) {
            if (quantity <= 0) {
                this.removeItem(itemId);
            } else {
                item.quantity = quantity;
                this.saveCart(cart);
            }
        }
    },
    
    // Clear cart
    clearCart() {
        localStorage.removeItem(this.STORAGE_KEY);
        this.updateDisplay();
    },
    
    // Update UI display
    updateDisplay() {
        const cart = this.getCart();
        const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0);
        const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        
        console.log('Cart:', cart);
        console.log('Cart Total:', cartTotal);
        
        // Update cart count badge
        const cartCountElement = document.getElementById('cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = cartCount;
        }
        
        // Update cart items display
        const cartItemsElement = document.getElementById('cart-items');
        if (cartItemsElement) {
            if (cart.length === 0) {
                cartItemsElement.innerHTML = '<p class="text-center text-muted p-3">Tu carrito está vacío</p>';
            } else {
                cartItemsElement.innerHTML = cart.map(item => {
                    const itemTotal = item.price * item.quantity;
                    return `
                        <div class="cart-item d-flex justify-content-between align-items-center p-2 border-bottom">
                            <div>
                                <h6 class="mb-0">${item.name}</h6>
                                <div class="d-flex align-items-center">
                                    <button class="btn btn-sm btn-outline-secondary me-2 decrease-quantity" data-id="${item.id}">-</button>
                                    <span class="quantity">${item.quantity}</span>
                                    <button class="btn btn-sm btn-outline-secondary ms-2 increase-quantity" data-id="${item.id}">+</button>
                                </div>
                                <small class="text-muted">${this._formatPrice(item.price)} x ${item.quantity} = ${this._formatPrice(itemTotal)}</small>
                            </div>
                            <div class="d-flex align-items-center">
                                <button class="btn btn-sm btn-outline-danger remove-item" data-id="${item.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
                
                // Attach event listeners to dynamically created buttons
                cartItemsElement.querySelectorAll('.decrease-quantity').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const itemId = e.target.dataset.id;
                        const item = cart.find(i => i.id == itemId);
                        if (item) {
                            this.updateQuantity(itemId, item.quantity - 1);
                        }
                    });
                });
                
                cartItemsElement.querySelectorAll('.increase-quantity').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const itemId = e.target.dataset.id;
                        const item = cart.find(i => i.id == itemId);
                        if (item) {
                            this.updateQuantity(itemId, item.quantity + 1);
                        }
                    });
                });
                
                cartItemsElement.querySelectorAll('.remove-item').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const itemId = e.target.closest('button').dataset.id;
                        this.removeItem(itemId);
                    });
                });
            }
        }
        
        // Update cart total - remove $ from _formatPrice since HTML already has it
        const cartTotalElement = document.getElementById('cart-total');
        if (cartTotalElement) {
            // Format without $ symbol since HTML already includes it
            const formattedTotal = new Intl.NumberFormat('es-CL', {
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(cartTotal);
            cartTotalElement.textContent = formattedTotal;
        }
    },
    
    // Format price helper
    _formatPrice(price) {
        return '$' + new Intl.NumberFormat('es-CL', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(price);
    },
    
    // Show toast helper
    _showToast(message, type = 'success') {
        if (window.Toast) {
            window.Toast[type](message);
        }
    }
};

// Initialize cart display on page load
document.addEventListener('DOMContentLoaded', function() {
    CartManager.updateDisplay();
    
    // Attach event listeners to add-to-cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.dataset.id;
            const itemName = this.dataset.name;
            const itemPrice = parseFloat(this.dataset.price);
            
            CartManager.addItem(itemId, itemName, itemPrice, 1);
        });
    });
    
    // Submit order function
    window.submitOrder = function() {
        const cart = CartManager.getCart();
        
        if (cart.length === 0) {
            CartManager._showToast('El carrito está vacío', 'warning');
            return;
        }

        // Get button and add loading state
        const submitButton = document.querySelector('[onclick="submitOrder()"]');
        let originalState = null;
        if (submitButton && window.LoadingState) {
            originalState = window.LoadingState.start(submitButton, 'Enviando pedido...');
        }

        // Get token from URL if exists
        const pathParts = window.location.pathname.split('/');
        const token = pathParts[pathParts.length - 1];

        // Prepare order data
        const orderData = {
            items: cart.map(item => ({
                id: item.id,
                quantity: item.quantity
            })),
            is_delivery: !token || token === 'delivery',
            token: token && token !== 'delivery' ? token : null
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
            // Restore button state
            if (submitButton && originalState && window.LoadingState) {
                window.LoadingState.stop(submitButton, originalState);
            }

            if (data.success) {
                CartManager._showToast('Pedido enviado correctamente', 'success');
                CartManager.clearCart();
                
                // Close modal
                const cartModal = bootstrap.Modal.getInstance(document.getElementById('cartModal'));
                if (cartModal) {
                    cartModal.hide();
                }
                
                // Redirect to confirmation page if URL provided
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                }
            } else {
                CartManager._showToast(data.error || 'Error al enviar el pedido', 'error');
            }
        })
        .catch(error => {
            // Restore button state
            if (submitButton && originalState && window.LoadingState) {
                window.LoadingState.stop(submitButton, originalState);
            }

            console.error('Error:', error);
            CartManager._showToast('Error al enviar el pedido', 'error');
        });
    };
});
