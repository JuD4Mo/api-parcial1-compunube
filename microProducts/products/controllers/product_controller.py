from flask import Blueprint, request, jsonify
from products.models.product_model import Products
from db.db import db
from decimal import Decimal, InvalidOperation

product_controller = Blueprint("product_controller", __name__)

@product_controller.route('/api/products', methods=['GET'])
def get_products():
	print("listado de productos")
	products = Products.query.all()
	result = [{'id': product.id, 'name': product.name, 'quantity': product.quantity, 'priceU': float(product.priceU) if product.priceU is not None else None} for product in products]
	return jsonify(result)

# Get single product by id
@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
	print("obteniendo producto")
	product = Products.query.get_or_404(product_id)
	return jsonify({'id': product.id, 'name': product.name, 'quantity': product.quantity, 'priceU': float(product.priceU) if product.priceU is not None else None})

@product_controller.route('/api/products', methods=['POST'])
def create_product():
	print("creando producto")
	data = request.json or {}
	try:
		name = data.get('name')
		if not name:
			return jsonify({'error': 'Missing product name'}), 400
		quantity = int(data.get('quantity', 0))
		try:
			price = Decimal(str(data.get('priceU', 0)))
		except (InvalidOperation, TypeError):
			return jsonify({'error': 'Invalid price format'}), 400

		new_product = Products(name=name, quantity=quantity, priceU=price)
		db.session.add(new_product)
		db.session.commit()
		return jsonify({'message': 'Product created successfully'}), 201
	except Exception as e:
		# Return a JSON error to avoid a 500 with no details in the client
		return jsonify({'error': str(e)}), 400

# Update an existing product
@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
	print("actualizando producto")
	product = Products.query.get_or_404(product_id)
	data = request.json or {}
	try:
		if 'name' in data:
			product.name = data.get('name')
		if 'quantity' in data:
			product.quantity = int(data.get('quantity', product.quantity))
		if 'priceU' in data:
			try:
				product.priceU = Decimal(str(data.get('priceU')))
			except (InvalidOperation, TypeError):
				return jsonify({'error': 'Invalid price format'}), 400
		db.session.commit()
		return jsonify({'message': 'Product updated successfully'})
	except Exception as e:
		return jsonify({'error': str(e)}), 400

# Delete an existing product
@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
	product = Products.query.get_or_404(product_id)
	db.session.delete(product)
	db.session.commit()
	return jsonify({'message': 'Product deleted successfully'})
