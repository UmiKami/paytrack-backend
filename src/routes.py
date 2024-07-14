from flask import Blueprint, jsonify, request
from src.models import db, User, Employee, PasswordResetToken
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from hashlib import sha256
import os

api = Blueprint('api', __name__)

@api.route("/hello", methods=["GET"])
def index():
    return jsonify(message="Welcome to PayTrack API v1.0!")

@api.route("/admin/register", methods=["POST"])
def regisster_admin():
    request_body = request.get_json()

    secret_key = request_body.get("secret_key")
    
    if secret_key != os.getenv("JWT_SECRET_KEY"):
        return jsonify(message="Invalid secret key"), 401
        
    email = request_body.get("email")
    password = request_body.get("password")
    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User(email=email, password_hash=password_hash, role="admin")
    db.session.add(user)
    db.session.commit()
    
    return jsonify(message="Admin user created successfully!")

@api.route("/admin/login", methods=["POST"])
def login_admin():
    request_body = request.get_json()
    
    email = request_body.get("email")
    password = request_body.get("password")
    
    password_hash = sha256(password.encode()).hexdigest()
    
    user = User.query.filter_by(email=email, password_hash=password_hash).first()
    
    if user is None:
        return jsonify(message="Invalid email or password"), 401
        
    access_token = create_access_token(identity=user.user_id)
    
    return jsonify(access_token=access_token)

