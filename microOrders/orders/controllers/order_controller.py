from flask import Blueprint, request, jsonify, session
from orders.models.order_model import Order, OrderItem
from db.db import db
from decimal import Decimal
import requests
import traceback
import os

order_controller = Blueprint('order_controller', __name__)

# Variables de entorno relacionadas a consul y a productos
CONSUL_HOST = os.environ.get("CONSUL_HOST", "consul")
CONSUL_PORT = os.environ.get("CONSUL_PORT", "8500")
PRODUCTS_SERVICE = os.environ.get("PRODUCTS_SERVICE", "micro-products")


def get_products_base():
    """
    Pregunta a Consul por el servicio micro-products y devuelve la URL base.
    http://micro-products:5003/api/products
    """
    url = f"http://{CONSUL_HOST}:{CONSUL_PORT}/v1/health/service/{PRODUCTS_SERVICE}?passing=true"
    resp = requests.get(url, timeout=2)

    if resp.status_code != 200:
        raise RuntimeError("No se pudo consultar Consul")

    data = resp.json()
    if not data:
        raise RuntimeError("No hay instancias disponibles de micro-products")

    service_info = data[0]["Service"]
    address = service_info.get("Address") or data[0]["Node"]["Address"]
    port = service_info["Port"]

    return f"http://{address}:{port}/api/products"


@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    result = []

    # Para GET: si products falla, no rompe (solo deja name=None)
    try:
        base = get_products_base()
    except Exception:
        base = None

    for o in orders:
        items = []
        for it in o.items:
            pname = None
            if base:
                try:
                    resp = requests.get(f"{base}/{it.product_id}")
                    if resp.status_code == 200:
                        pname = resp.json().get('name')
                except Exception:
                    pname = None

            items.append({
                'product_id': it.product_id,
                'name': pname,
                'quantity': it.quantity,
                'unit_price': float(it.unit_price)
            })

        result.append({
            'id': o.id,
            'user': {'id': o.user_id, 'name': o.user_name, 'email': o.user_email},
            'total': float(o.total),
            'created_at': o.created_at.isoformat(),
            'products': items
        })

    return jsonify(result)


@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    o = Order.query.get_or_404(order_id)

    try:
        base = get_products_base()
    except Exception:
        base = None

    items = []
    for it in o.items:
        pname = None
        if base:
            try:
                resp = requests.get(f"{base}/{it.product_id}")
                if resp.status_code == 200:
                    pname = resp.json().get('name')
            except Exception:
                pname = None

        items.append({
            'product_id': it.product_id,
            'name': pname,
            'quantity': it.quantity,
            'unit_price': float(it.unit_price)
        })

    return jsonify({
        'id': o.id,
        'user': {'id': o.user_id, 'name': o.user_name, 'email': o.user_email},
        'total': float(o.total),
        'created_at': o.created_at.isoformat(),
        'products': items
    })


@order_controller.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json() or {}

    user_id = session.get('user_id')
    user_name = session.get('username')
    user_email = session.get('email')
    if not user_id or not user_name or not user_email:
        return jsonify({'message': 'Autenticación requerida'}), 401

    products = data.get('products')
    if not products or not isinstance(products, list):
        return jsonify({'message': 'Falta o es inválida la información de los productos'}), 400

    # Para POST sí necesitamos products funcionando
    try:
        base = get_products_base()
    except Exception as e:
        return jsonify({'message': 'Servicio de productos no disponible', 'error': str(e)}), 503

    total = Decimal('0')
    validated = []

    for p in products:
        try:
            pid = int(p.get('id'))
            qty = int(p.get('quantity'))
        except Exception:
            return jsonify({'message': 'Producto inválido en la lista'}), 400

        resp = requests.get(f"{base}/{pid}")
        if resp.status_code != 200:
            return jsonify({'message': f'Producto {pid} no encontrado'}), 404

        prod = resp.json()
        available = int(prod.get('quantity', 0))
        price = Decimal(str(prod.get('priceU', 0)))

        if qty <= 0:
            return jsonify({'message': f'Cantidad inválida para producto {pid}'}), 400
        if qty > available:
            return jsonify({'message': f'Producto {pid} no tiene suficiente stock'}), 400

        validated.append({
            'id': pid,
            'quantity': qty,
            'available': available,
            'price': price,
            'name': prod.get('name')
        })
        total += price * qty

    # Actualizar inventario
    for item in validated:
        new_qty = item['available'] - item['quantity']
        update_payload = {'name': item['name'], 'quantity': new_qty, 'priceU': float(item['price'])}
        resp = requests.put(f"{base}/{item['id']}", json=update_payload)
        if resp.status_code not in (200, 201):
            return jsonify({'message': f'Error actualizando inventario para producto {item["id"]}'}), 500

    try:
        order = Order(user_name=user_name, user_email=user_email, total=total, user_id=user_id)
        db.session.add(order)
        db.session.flush()

        for item in validated:
            oi = OrderItem(order_id=order.id, product_id=item['id'], quantity=item['quantity'], unit_price=item['price'])
            db.session.add(oi)

        db.session.commit()
        return jsonify({'message': 'Orden creada exitosamente', 'order_id': order.id}), 201

    except Exception as e:
        db.session.rollback()

        restore_errors = []
        for item in validated:
            try:
                restore_payload = {'name': item.get('name'), 'quantity': item.get('available'), 'priceU': float(item.get('price'))}
                requests.put(f"{base}/{item['id']}", json=restore_payload)
            except Exception as re:
                restore_errors.append(str(re))

        tb = traceback.format_exc()
        return jsonify({'message': 'Error creando la orden', 'error': str(e), 'trace': tb, 'restore_errors': restore_errors}), 500


@order_controller.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    o = Order.query.get_or_404(order_id)

    # Para DELETE: idealmente products disponible para restaurar inventario
    try:
        base = get_products_base()
    except Exception as e:
        return jsonify({'message': 'Servicio de productos no disponible para restaurar inventario', 'error': str(e)}), 503

    for it in o.items:
        try:
            resp = requests.get(f"{base}/{it.product_id}")
            if resp.status_code == 200:
                prod = resp.json()
                cur_qty = int(prod.get('quantity', 0))
                new_qty = cur_qty + it.quantity
                update_payload = {'name': prod.get('name'), 'quantity': new_qty, 'priceU': prod.get('priceU')}
                requests.put(f"{base}/{it.product_id}", json=update_payload)
        except Exception:
            pass

    db.session.delete(o)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'})