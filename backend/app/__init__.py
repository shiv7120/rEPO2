import os
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, jsonify

from .extensions import db, migrate, jwt, cors


def create_app():
	load_dotenv()

	app = Flask(__name__)

	base_dir = os.path.abspath(os.path.dirname(__file__))
	db_path = os.path.join(base_dir, '..', 'bank.db')
	app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{os.path.abspath(db_path)}")
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-change-me')
	app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

	# Initialize extensions
	db.init_app(app)
	migrate.init_app(app, db)
	jwt.init_app(app)
	cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

	# Import models to register with SQLAlchemy before migrations
	from . import models  # noqa: F401

	# Register blueprints
	from .routes.auth import auth_bp
	from .routes.accounts import accounts_bp
	app.register_blueprint(auth_bp)
	app.register_blueprint(accounts_bp)

	# Error handlers
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({"message": "Not Found"}), 404

	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({"message": "Bad Request"}), 400

	@app.errorhandler(500)
	def server_error(error):
		return jsonify({"message": "Internal Server Error"}), 500

	return app