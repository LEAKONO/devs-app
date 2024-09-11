from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from models import User
from schemas import UserSchema
from utils import send_email  

auth = Blueprint('auth', __name__)

# User Registration Route
@auth.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    password = data['password']
    email = data['email']
    role = data['role']  
    
    if role not in ['customer', 'seller']:
        return jsonify({"error": "Invalid role"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
    
    db.session.add(new_user)
    db.session.commit()

    # Notify admin if a seller is registered
    if role == 'seller':
        admin_email = current_app.config['ADMIN_EMAIL']
        if admin_email:
            send_email("New Seller Registration", admin_email, f"New seller registered: {username}. Please approve their account.")

    return jsonify({"message": "User registered successfully"}), 201

# User Login Route
@auth.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token)

# Get User Info Route
@auth.route('/user', methods=['GET'])
@jwt_required()
def get_user_info():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify(UserSchema().dump(user))

# Get All Users (Admin Only)
@auth.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get_or_404(current_user_id)
    
    if current_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403

    users = User.query.all()
    return jsonify(UserSchema(many=True).dump(users))

# Admin Approval Route (Admin Only)
@auth.route('/sellers/approve/<int:user_id>', methods=['POST'])
@jwt_required()
def approve_seller(user_id):
    current_user_id = get_jwt_identity()
    admin_user = User.query.get_or_404(current_user_id)
    
    if admin_user.role != 'admin':
        return jsonify({"error": "Access denied"}), 403

    user = User.query.get_or_404(user_id)
    if user.role != 'seller':
        return jsonify({"error": "Not a seller"}), 400

    user.is_approved = True
    db.session.commit()

    # Notify seller
    send_email("Seller Account Approved", user.email, "Your seller account has been approved.")

    return jsonify({"message": "Seller approved successfully"})


