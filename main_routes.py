from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Product, Order, Cart, Complaint, Feedback, User
from schemas import ProductSchema, OrderSchema, CartSchema, ComplaintSchema, FeedbackSchema
from utils import send_email 

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/products', methods=['POST'])
@jwt_required()
def add_product():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != 'seller':
        return jsonify({"error": "Access denied"}), 403

    data = request.json
    new_product = Product(name=data['name'], price=data['price'], seller_id=user_id)
    db.session.add(new_product)
    db.session.commit()

    return jsonify(ProductSchema().dump(new_product))

@main_routes.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify(ProductSchema(many=True).dump(products))

@main_routes.route('/products/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != 'seller':
        return jsonify({"error": "Access denied"}), 403

    data = request.json
    product = Product.query.get_or_404(product_id)
    if product.seller_id != user_id:
        return jsonify({"error": "Access denied"}), 403

    product.name = data['name']
    product.price = data['price']
    db.session.commit()
    return jsonify(ProductSchema().dump(product))

@main_routes.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role != 'seller':
        return jsonify({"error": "Access denied"}), 403

    product = Product.query.get_or_404(product_id)
    if product.seller_id != user_id:
        return jsonify({"error": "Access denied"}), 403

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

@main_routes.route('/orders', methods=['POST'])
@jwt_required()
def place_order():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role == 'admin' or user.role == 'seller':
        return jsonify({"error": "Access denied"}), 403

    data = request.json
    new_order = Order(product_id=data['product_id'], quantity=data['quantity'], user_id=user_id)
    db.session.add(new_order)
    db.session.commit()

    # Notify seller
    product = Product.query.get_or_404(data['product_id'])
    seller = User.query.get_or_404(product.seller_id)
    send_email("New Order", seller.email, f"New order for product {product.name}")

    return jsonify(OrderSchema().dump(new_order))

@main_routes.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    
    if user.role == 'seller':
        orders = Order.query.filter_by(seller_id=user_id).all()
    else:
        orders = Order.query.filter_by(user_id=user_id).all()
    
    return jsonify(OrderSchema(many=True).dump(orders))

# Cart Routes
@main_routes.route('/carts', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json
    product_id = data['product_id']
    quantity = data['quantity']
    
    item = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        new_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({"message": "Item added to cart"})

@main_routes.route('/carts', methods=['GET'])
@jwt_required()
def get_cart():
    user_id = get_jwt_identity()
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    return jsonify(CartSchema(many=True).dump(cart_items))

# Complaint Routes
@main_routes.route('/complaints', methods=['POST'])
@jwt_required()
def file_complaint():
    user_id = get_jwt_identity()
    data = request.json
    new_complaint = Complaint(user_id=user_id, description=data['description'])
    db.session.add(new_complaint)
    db.session.commit()

    # Notify admin
    admin_email = current_app.config['ADMIN_EMAIL']
    if admin_email:
        send_email("New Complaint", admin_email, f"New complaint from user {user_id}")

    return jsonify(ComplaintSchema().dump(new_complaint))


# Feedback Routes
@main_routes.route('/feedbacks', methods=['POST'])
@jwt_required()
def leave_feedback():
    user_id = get_jwt_identity()
    data = request.json
    new_feedback = Feedback(
        user_id=user_id,
        product_id=data['product_id'],
        rating=data['rating'],
        comment=data.get('comment')
    )
    db.session.add(new_feedback)
    db.session.commit()
    return jsonify(FeedbackSchema().dump(new_feedback))

@main_routes.route('/feedbacks/<int:product_id>', methods=['GET'])
def get_feedback(product_id):
    feedbacks = Feedback.query.filter_by(product_id=product_id).all()
    return jsonify(FeedbackSchema(many=True).dump(feedbacks))
