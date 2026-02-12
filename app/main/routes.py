from flask import render_template, redirect, url_for, jsonify, request
from app.main import bp
from app.models import MenuItem, TableToken, Order, OrderItem, db
from app import socketio
from flask_socketio import emit
from datetime import datetime

def create_order_from_token(token_string, customer_name, instructions, items):
    """
    Create order with table number from token.
    
    Args:
        token_string: Token string from QR code
        customer_name: Name of customer (optional)
        instructions: Special instructions (optional)
        items: List of dicts with 'id' and 'quantity' keys
        
    Returns:
        Order instance or None if token invalid
    """
    # Lookup token and extract table number
    token = TableToken.query.filter_by(
        token=token_string,
        is_active=True
    ).first()
    
    # Verify token exists, is active, has table number, and not expired
    if not token or not token.table_number:
        return None
    
    # Check if token has expired (if session times are set)
    if token.session_end and datetime.utcnow() > token.session_end:
        return None
    
    # Calculate total
    total = 0
    order_items_data = []
    
    for item_data in items:
        menu_item = MenuItem.query.get(int(item_data['id']))
        if not menu_item:
            return None
        
        quantity = int(item_data['quantity'])
        total += menu_item.price * quantity
        order_items_data.append((menu_item, quantity))
    
    # Create order with table number
    order = Order(
        table_number=token.table_number,
        status='pending',
        total=total,
        is_delivery=False,
        timestamp=datetime.utcnow()
    )
    db.session.add(order)
    
    # Add order items
    for menu_item, quantity in order_items_data:
        order_item = OrderItem(
            order=order,
            menu_item_id=menu_item.id,
            quantity=quantity
        )
        db.session.add(order_item)
    
    db.session.commit()
    return order

@bp.route('/')
@bp.route('/index')
def index():
    # Redirigir al panel de admin
    return redirect(url_for('admin.qr_generator'))

@bp.route('/delivery')
def delivery_menu():
    menu_items = MenuItem.query.all()
    return render_template('menu/delivery_menu.html', menu_items=menu_items)

@bp.route('/menu/<token>')
def menu(token):
    # Buscar el token en la base de datos
    table_token = TableToken.query.filter_by(token=token).first()
    
    # Si el token no existe o no es válido, redirigir al menú de delivery
    if not table_token or not table_token.is_valid():
        return redirect(url_for('main.delivery_menu'))
    
    # Actualizar último uso
    table_token.last_used = datetime.utcnow()
    db.session.commit()
    
    # Query MenuItem table for all active items
    menu_items = MenuItem.query.filter_by(available=True).all()
    
    # Group items by category
    categories = {}
    for item in menu_items:
        category = item.category or 'Other'
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    return render_template('menu/table_menu.html', 
                         categories=categories,
                         token=token,
                         table_number=table_token.table_number)

@bp.route('/payment')
def payment_page():
    return render_template('payment.html')

@bp.route('/order/confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Display order confirmation page"""
    # Query Order with order_id
    order = Order.query.get_or_404(order_id)
    
    # Calculate total from order items
    total = sum(item.menu_item.price * item.quantity for item in order.items)
    
    # Render confirmation template with order data
    return render_template(
        'menu/order_confirmation.html',
        order=order,
        total=total
    )

@bp.route('/create_order', methods=['POST'])
def create_order():
    print("Recibiendo pedido...")  # Debug print
    try:
        data = request.get_json()
        print(f"Datos recibidos: {data}")  # Debug print
        
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400

        items = data.get('items', [])
        is_delivery = data.get('is_delivery', False)
        token = data.get('token')
        
        print(f"Items: {items}")  # Debug print
        print(f"Is delivery: {is_delivery}")  # Debug print
        print(f"Token: {token}")  # Debug print
        
        if not items:
            return jsonify({'error': 'No hay items en el pedido'}), 400
        
        # Handle delivery orders (legacy path)
        if is_delivery:
            table_number = data.get('table_number', 0)
            
            # Calculate total
            total = 0
            order_items = []
            
            for item_data in items:
                menu_item = MenuItem.query.get(int(item_data['id']))
                if not menu_item:
                    return jsonify({'error': f'Item con ID {item_data["id"]} no encontrado'}), 404
                    
                quantity = int(item_data['quantity'])
                total += menu_item.price * quantity
                order_items.append((menu_item, quantity))
            
            # Create the order
            order = Order(
                table_number=table_number,
                status='pending',
                total=total,
                is_delivery=is_delivery,
                timestamp=datetime.utcnow()
            )
            db.session.add(order)
            
            # Add items to the order
            for menu_item, quantity in order_items:
                order_item = OrderItem(
                    order=order,
                    menu_item_id=menu_item.id,
                    quantity=quantity
                )
                db.session.add(order_item)
            
            db.session.commit()
            print(f"Orden creada con ID: {order.id}")  # Debug print
        else:
            # Handle table orders using token
            if not token:
                return jsonify({'error': 'Token requerido para pedidos de mesa'}), 400
            
            # Use the new helper function
            order = create_order_from_token(
                token_string=token,
                customer_name=data.get('customer_name', ''),
                instructions=data.get('special_instructions', ''),
                items=items
            )
            
            if not order:
                return jsonify({'error': 'Token inválido o mesa no encontrada'}), 400
            
            print(f"Orden creada con ID: {order.id}")  # Debug print

        # Emit WebSocket event to notify kitchen
        socketio.emit('new_order', {
            'order_id': order.id,
            'table_number': order.table_number,
            'is_delivery': order.is_delivery,
            'total': order.total
        }, namespace='/')

        return jsonify({
            'success': True,
            'order_id': order.id,
            'redirect_url': url_for('main.order_confirmation', order_id=order.id, token=token if not is_delivery else ''),
            'message': 'Pedido creado exitosamente'
        })
            
    except Exception as e:
        db.session.rollback()
        print(f"Error al procesar el pedido: {str(e)}")  # Debug print
        return jsonify({'error': f'Error al procesar el pedido: {str(e)}'}), 500
