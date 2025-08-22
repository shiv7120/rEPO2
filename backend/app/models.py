import enum
import random
import string
from datetime import datetime
from decimal import Decimal

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Numeric, Enum

from .extensions import db


class AccountType(enum.Enum):
	checking = 'checking'
	savings = 'savings'


class TransactionType(enum.Enum):
	deposit = 'deposit'
	withdraw = 'withdraw'
	transfer_in = 'transfer_in'
	transfer_out = 'transfer_out'


class User(db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False, index=True)
	full_name = db.Column(db.String(255), nullable=False)
	password_hash = db.Column(db.String(255), nullable=False)
	date_joined = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	accounts = db.relationship('Account', backref='user', lazy=True)

	def set_password(self, password: str) -> None:
		self.password_hash = generate_password_hash(password)

	def check_password(self, password: str) -> bool:
		return check_password_hash(self.password_hash, password)

	def to_dict(self):
		return {
			"id": self.id,
			"email": self.email,
			"full_name": self.full_name,
			"date_joined": self.date_joined.isoformat(),
		}


class Account(db.Model):
	__tablename__ = 'accounts'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
	account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
	account_type = db.Column(Enum(AccountType), nullable=False, default=AccountType.checking)
	balance = db.Column(Numeric(12, 2), nullable=False, default=Decimal('0.00'))
	created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	transactions = db.relationship('Transaction', backref='account', lazy=True)

	@staticmethod
	def generate_account_number() -> str:
		# 12-digit pseudo-random number
		return ''.join(random.choices(string.digits, k=12))

	def to_dict(self):
		return {
			"id": self.id,
			"user_id": self.user_id,
			"account_number": self.account_number,
			"account_type": self.account_type.value,
			"balance": float(self.balance),
			"created_at": self.created_at.isoformat(),
		}


class Transaction(db.Model):
	__tablename__ = 'transactions'

	id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False, index=True)
	transaction_type = db.Column(Enum(TransactionType), nullable=False)
	amount = db.Column(Numeric(12, 2), nullable=False)
	description = db.Column(db.String(255), nullable=True)
	related_account_id = db.Column(db.Integer, nullable=True)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

	def to_dict(self):
		return {
			"id": self.id,
			"account_id": self.account_id,
			"transaction_type": self.transaction_type.value,
			"amount": float(self.amount),
			"description": self.description,
			"related_account_id": self.related_account_id,
			"timestamp": self.timestamp.isoformat(),
		}