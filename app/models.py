from datetime import datetime
from app import db
import random

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(64), nullable=False)
    available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(256))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy=True)
    total = db.Column(db.Float, nullable=False)
    is_delivery = db.Column(db.Boolean, default=False)
    delivery_address = db.Column(db.String(256))
    customer_phone = db.Column(db.String(20))

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(256))
    
    # Add relationship to MenuItem
    menu_item = db.relationship('MenuItem', backref='order_items', lazy=True)

class TableToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer, nullable=False)
    token = db.Column(db.String(64), unique=True, nullable=False)
    activation_code = db.Column(db.String(6), nullable=True)  # Código de 6 dígitos
    session_active = db.Column(db.Boolean, default=False)
    session_start = db.Column(db.DateTime, nullable=True)
    session_end = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_used = db.Column(db.DateTime)
    
    def is_valid(self):
        """Verificar si el token es válido basado en reglas de negocio"""
        if not self.is_active or not self.session_active:
            return False
            
        # Verificar si la sesión está activa y dentro del tiempo límite
        if self.session_start and self.session_end:
            now = datetime.utcnow()
            if now < self.session_start or now > self.session_end:
                return False
                
        return True

    def generate_activation_code(self):
        """Genera un código de activación de 6 dígitos"""
        self.activation_code = ''.join(random.choices('0123456789', k=6))
        self.session_active = False
        self.session_start = None
        self.session_end = None
        return self.activation_code

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(64), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
