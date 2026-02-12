from datetime import datetime, timedelta
from flask import render_template, jsonify, request, current_app
from app.admin import bp
from app.models import Order, MenuItem, TableToken
from app import db
import qrcode
import base64
from io import BytesIO
import secrets

def generate_table_token():
    return secrets.token_urlsafe(32)

def get_or_create_table_token(table_number):
    """
    Get existing active token for table or create new one.
    
    Args:
        table_number: Integer table number
        
    Returns:
        TableToken instance (existing or newly created)
    """
    # Check for existing active token
    existing_token = TableToken.query.filter_by(
        table_number=table_number,
        is_active=True
    ).first()
    
    if existing_token:
        return existing_token
    
    # Create new token only if none exists
    new_token = TableToken(
        token=generate_table_token(),
        table_number=table_number,
        is_active=True
    )
    
    # Generate activation code
    new_token.generate_activation_code()
    
    db.session.add(new_token)
    db.session.commit()
    
    return new_token

@bp.route('/qrgen')
def qr_generator():
    return render_template('admin/qr_generator.html', current_time=datetime.now())

@bp.route('/generate_table_qr', methods=['POST'])
def generate_table_qr():
    try:
        data = request.json
        table_number = data.get('table_number')
        
        if not table_number:
            return jsonify({'error': 'Número de mesa requerido'}), 400
            
        # Get or create token for the table
        table_token = get_or_create_table_token(table_number)
        
        # Create URL with the token
        base_url = request.host_url.rstrip('/')
        url = f"{base_url}/menu/{table_token.token}"
        
        # Generar código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir imagen a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'qr_code': img_str,
            'token': table_token.token,
            'url': url,
            'activation_code': table_token.activation_code
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/activate_table', methods=['POST'])
def activate_table():
    data = request.json
    token = data.get('token')
    activation_code = data.get('activation_code')
    duration_minutes = int(data.get('duration', 120))  # Default 2 hours
    
    if not token or not activation_code:
        return jsonify({'error': 'Token and activation code are required'}), 400
    
    table_token = TableToken.query.filter_by(token=token).first()
    
    if not table_token:
        return jsonify({'error': 'Invalid token'}), 404
        
    if table_token.activation_code != activation_code:
        return jsonify({'error': 'Invalid activation code'}), 400
    
    if not table_token.is_active:
        return jsonify({'error': 'Table is not active'}), 400
    
    now = datetime.utcnow()
    
    # Activar la sesión
    table_token.session_active = True
    table_token.session_start = now
    table_token.session_end = now + timedelta(minutes=duration_minutes)
    table_token.last_used = now
    
    try:
        db.session.commit()
        return jsonify({
            'success': True,
            'table_number': table_token.table_number,
            'session_start': table_token.session_start.isoformat(),
            'session_end': table_token.session_end.isoformat()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/active_tables')
def get_active_tables():
    active_tables = TableToken.query.filter_by(session_active=True).all()
    tables_data = [{
        'table_number': table.table_number,
        'token': table.token,
        'session_start': table.session_start.isoformat() if table.session_start else None,
        'session_end': table.session_end.isoformat() if table.session_end else None
    } for table in active_tables if table.session_end and table.session_end > datetime.utcnow()]
    
    return jsonify({'tables': tables_data})

@bp.route('/deactivate_table', methods=['POST'])
def deactivate_table():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No se recibieron datos'}), 400
            
        table_number = data.get('table_number')
        if not table_number:
            return jsonify({'error': 'Número de mesa requerido'}), 400
            
        # Convertir a entero si es string
        if isinstance(table_number, str):
            table_number = int(table_number)
        
        # Buscar el token activo más reciente para esta mesa
        table_token = TableToken.query.filter_by(
            table_number=table_number,
            session_active=True
        ).order_by(TableToken.created_at.desc()).first()
        
        if not table_token:
            return jsonify({'error': 'Mesa no encontrada o ya desactivada'}), 400
        
        # Desactivar la sesión
        table_token.session_active = False
        table_token.session_end = datetime.utcnow()
        
        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'Mesa {table_number} desactivada correctamente'
        })
        
    except ValueError as e:
        return jsonify({'error': 'Número de mesa inválido'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/kitchen')
def kitchen():
    return render_template('admin/kitchen.html', current_time=datetime.now())

@bp.route('/kitchen/orders')
def get_kitchen_orders():
    # Obtener órdenes activas (no completadas)
    active_orders = Order.query.filter_by(
        is_delivery=False,
        status='pending'
    ).order_by(Order.timestamp.desc()).all()
    
    orders_data = []
    for order in active_orders:
        items = []
        total = 0
        for item in order.items:
            menu_item = MenuItem.query.get(item.menu_item_id)
            item_data = {
                'name': menu_item.name,
                'quantity': item.quantity,
                'price': menu_item.price
            }
            items.append(item_data)
            total += menu_item.price * item.quantity
            
        orders_data.append({
            'id': order.id,
            'table_number': order.table_number,
            'created_at': order.timestamp.isoformat(),
            'items': items,
            'total': total
        })
    
    return jsonify({'orders': orders_data})

@bp.route('/kitchen/complete_order', methods=['POST'])
def complete_order():
    data = request.json
    order_id = data.get('order_id')
    
    if not order_id:
        return jsonify({'error': 'ID de orden requerido'}), 400
    
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'error': 'Orden no encontrada'}), 404
    
    order.status = 'completed'
    db.session.commit()
    
    return jsonify({'success': True})
