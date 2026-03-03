from datetime import datetime
from db.db import db
from decimal import Decimal


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable=False)
    total = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    def __init__(self, user_name, user_email, total, user_id=None):
        self.user_id = user_id
        self.user_name = user_name
        self.user_email = user_email
        self.total = Decimal(total)


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10,2), nullable=False)

    def __init__(self, order_id, product_id, quantity, unit_price):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = Decimal(unit_price)
