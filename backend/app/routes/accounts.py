from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..extensions import db
from ..models import Account, Transaction, TransactionType, AccountType, User


accounts_bp = Blueprint('accounts', __name__, url_prefix='/api')


def _get_current_user():
	user_id = get_jwt_identity()
	return User.query.get(int(user_id))


def _parse_amount(value):
	try:
		amount = Decimal(str(value))
		if amount <= 0:
			raise InvalidOperation()
		return amount
	except Exception:
		return None


@accounts_bp.get('/accounts')
@jwt_required()
def list_accounts():
	user = _get_current_user()
	accounts = Account.query.filter_by(user_id=user.id).order_by(Account.created_at.desc()).all()
	return jsonify([a.to_dict() for a in accounts])


@accounts_bp.post('/accounts')
@jwt_required()
def create_account():
	user = _get_current_user()
	data = request.get_json(silent=True) or {}
	account_type_str = (data.get('account_type') or 'checking').lower()
	if account_type_str not in ('checking', 'savings'):
		return jsonify({"message": "account_type must be 'checking' or 'savings'"}), 400

	account = Account(
		user_id=user.id,
		account_number=Account.generate_account_number(),
		account_type=AccountType[account_type_str]
	)
	db.session.add(account)
	db.session.commit()
	return jsonify(account.to_dict()), 201


@accounts_bp.post('/accounts/<int:account_id>/deposit')
@jwt_required()
def deposit(account_id: int):
	user = _get_current_user()
	account = Account.query.get_or_404(account_id)
	if account.user_id != user.id:
		return jsonify({"message": "Forbidden"}), 403

	data = request.get_json(silent=True) or {}
	amount = _parse_amount(data.get('amount'))
	if amount is None:
		return jsonify({"message": "Invalid amount"}), 400

	account.balance = (account.balance or Decimal('0.00')) + amount

	tx = Transaction(
		account_id=account.id,
		transaction_type=TransactionType.deposit,
		amount=amount,
		description=data.get('description')
	)
	db.session.add(tx)
	db.session.commit()
	return jsonify({"account": account.to_dict(), "transaction": tx.to_dict()})


@accounts_bp.post('/accounts/<int:account_id>/withdraw')
@jwt_required()
def withdraw(account_id: int):
	user = _get_current_user()
	account = Account.query.get_or_404(account_id)
	if account.user_id != user.id:
		return jsonify({"message": "Forbidden"}), 403

	data = request.get_json(silent=True) or {}
	amount = _parse_amount(data.get('amount'))
	if amount is None:
		return jsonify({"message": "Invalid amount"}), 400

	if account.balance < amount:
		return jsonify({"message": "Insufficient funds"}), 400

	account.balance = account.balance - amount

	tx = Transaction(
		account_id=account.id,
		transaction_type=TransactionType.withdraw,
		amount=amount,
		description=data.get('description')
	)
	db.session.add(tx)
	db.session.commit()
	return jsonify({"account": account.to_dict(), "transaction": tx.to_dict()})


@accounts_bp.post('/accounts/transfer')
@jwt_required()
def transfer():
	user = _get_current_user()
	data = request.get_json(silent=True) or {}
	from_account_id = data.get('from_account_id')
	to_account_number = (data.get('to_account_number') or '').strip()
	amount = _parse_amount(data.get('amount'))
	if not from_account_id or not to_account_number or amount is None:
		return jsonify({"message": "from_account_id, to_account_number, amount are required"}), 400

	from_account: Account = Account.query.get_or_404(int(from_account_id))
	if from_account.user_id != user.id:
		return jsonify({"message": "Forbidden"}), 403

	to_account: Account = Account.query.filter_by(account_number=to_account_number).first()
	if to_account is None:
		return jsonify({"message": "Destination account not found"}), 404
	if from_account.id == to_account.id:
		return jsonify({"message": "Cannot transfer to the same account"}), 400
	if from_account.balance < amount:
		return jsonify({"message": "Insufficient funds"}), 400

	# Perform transfer
	from_account.balance = from_account.balance - amount
	to_account.balance = (to_account.balance or Decimal('0.00')) + amount

	out_tx = Transaction(
		account_id=from_account.id,
		transaction_type=TransactionType.transfer_out,
		amount=amount,
		description=data.get('description'),
		related_account_id=to_account.id,
	)
	in_tx = Transaction(
		account_id=to_account.id,
		transaction_type=TransactionType.transfer_in,
		amount=amount,
		description=data.get('description'),
		related_account_id=from_account.id,
	)
	db.session.add(out_tx)
	db.session.add(in_tx)
	db.session.commit()
	return jsonify({
		"from_account": from_account.to_dict(),
		"to_account": to_account.to_dict(),
		"transactions": [out_tx.to_dict(), in_tx.to_dict()],
	})


@accounts_bp.get('/accounts/<int:account_id>/transactions')
@jwt_required()
def list_transactions(account_id: int):
	user = _get_current_user()
	account = Account.query.get_or_404(account_id)
	if account.user_id != user.id:
		return jsonify({"message": "Forbidden"}), 403
	limit = int((request.args.get('limit') or 50))
	txs = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.timestamp.desc()).limit(limit).all()
	return jsonify([t.to_dict() for t in txs])