from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from ..extensions import db
from ..models import User


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.post('/register')
def register():
	data = request.get_json(silent=True) or {}
	email = (data.get('email') or '').strip().lower()
	full_name = (data.get('full_name') or '').strip()
	password = data.get('password') or ''

	if not email or not full_name or not password:
		return jsonify({"message": "email, full_name, and password are required"}), 400

	if User.query.filter_by(email=email).first() is not None:
		return jsonify({"message": "Email already registered"}), 400

	user = User(email=email, full_name=full_name)
	user.set_password(password)
	db.session.add(user)
	db.session.commit()

	access_token = create_access_token(identity=str(user.id))
	return jsonify({"access_token": access_token, "user": user.to_dict()}), 201


@auth_bp.post('/login')
def login():
	data = request.get_json(silent=True) or {}
	email = (data.get('email') or '').strip().lower()
	password = data.get('password') or ''

	if not email or not password:
		return jsonify({"message": "email and password are required"}), 400

	user = User.query.filter_by(email=email).first()
	if user is None or not user.check_password(password):
		return jsonify({"message": "Invalid credentials"}), 401

	access_token = create_access_token(identity=str(user.id))
	return jsonify({"access_token": access_token, "user": user.to_dict()})


@auth_bp.get('/me')
@jwt_required()
def me():
	user_id = get_jwt_identity()
	user = User.query.get(int(user_id))
	if user is None:
		return jsonify({"message": "User not found"}), 404
	return jsonify(user.to_dict())