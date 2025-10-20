from flask import render_template, redirect, url_for, jsonify, request
from app.main import bp
from app.models import MenuItem, TableToken, Order, OrderItem, db
from app import socketio
from flask_socketio import emit
from datetime import datetime

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
    
    # Obtener los ítems del menú
    menu_items = MenuItem.query.all()
    return render_template('menu/table_menu.html', 
                         menu_items=menu_items, 
                         table_number=table_token.table_number)

@bp.route('/payment')
def payment_page():
    return render_template('payment.html')

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
        table_number = data.get('table_number')
        
        print(f"Items: {items}")  # Debug print
        print(f"Is delivery: {is_delivery}")  # Debug print
        print(f"Table number: {table_number}")  # Debug print
        
        if not items:
            return jsonify({'error': 'No hay items en el pedido'}), 400
            
        # Calcular el total
        total = 0
        order_items = []
        
        for item_data in items:
            menu_item = MenuItem.query.get(int(item_data['id']))
            if not menu_item:
                return jsonify({'error': f'Item con ID {item_data["id"]} no encontrado'}), 404
                
            quantity = int(item_data['quantity'])
            total += menu_item.price * quantity
            order_items.append((menu_item, quantity))
        
        # Crear la orden
        order = Order(
            table_number=table_number if table_number else 0,  # Usar 0 para delivery
            status='pending',
            total=total,
            is_delivery=is_delivery,
            timestamp=datetime.utcnow()
        )
        db.session.add(order)
        
        # Agregar items a la orden
        for menu_item, quantity in order_items:
            order_item = OrderItem(
                order=order,
                menu_item_id=menu_item.id,
                quantity=quantity
            )
            db.session.add(order_item)
        
        db.session.commit()
        print(f"Orden creada con ID: {order.id}")  # Debug print

        # Emitir evento de WebSocket para notificar a la cocina
        socketio.emit('new_order', {
            'order_id': order.id,
            'table_number': order.table_number,
            'is_delivery': order.is_delivery,
            'total': order.total
        }, namespace='/')

        return jsonify({
            'success': True,
            'order_id': order.id,
            'message': 'Pedido creado exitosamente'
        })
            
    except Exception as e:
        db.session.rollback()
        print(f"Error al procesar el pedido: {str(e)}")  # Debug print
        return jsonify({'error': f'Error al procesar el pedido: {str(e)}'}), 500
