from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import User, Expense
from .utils import validate_date_format, validate_recurrence_flag, convert_to_iso

bp = Blueprint('routes', __name__)

@bp.route('/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    # ... validation ...
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']
    existing_user = User.get_by_username(username)
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 409

    user = User(username = username, password_hash = None)
    user.set_password(password)
    user.save()
    return jsonify({'message': 'User registered successfully'}), 201

@bp.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    # ... validation ...
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Missing username or password'}), 400

    username = data['username']
    password = data['password']
    user = User.get_by_username(username)

    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify({'access_token': access_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@bp.route('/expenses', methods=['POST'])
@jwt_required()
def create_expense():
    data = request.get_json()

    # ... validation ...
    required_fields = ['amount', 'description', 'date', 'category', 'recurrence_flag']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields', 'required_fields': required_fields}), 400
    if not isinstance(data['amount'], (int, float)):
        return jsonify({'error': 'Amount must be a number'}), 400
    if not isinstance(data['description'], str):
        return jsonify({'error': 'Description must be a string'}), 400
    if not isinstance(data['date'], str):
        return jsonify({'error': 'Date must be a string'}), 400
    if not isinstance(data['category'], str):
        return jsonify({'error': 'Category must be a string'}), 400
    if not validate_date_format(data['date']):
        return jsonify({'error': 'Invalid date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
    if not isinstance(data['recurrence_flag'], str):
        return jsonify({'error': 'Recurrence flag must be a string'}), 400
    if not validate_recurrence_flag(data['recurrence_flag']):
        return jsonify({'error': 'Invalid recurrence flag'}), 400
    # Convert to full ISO 8601 (handling date-only)
    date_iso = convert_to_iso(data['date'])

    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)  # Use model to get user

    expense = Expense(user_id=user.id, amount=data['amount'], description=data['description'], date=date_iso, category=data['category'], recurrence_flag=data['recurrence_flag'])
    expense.save()

    return jsonify({'id': expense.id, 'user_id': expense.user_id, 'amount': expense.amount, 'description': expense.description, 'date': expense.date, 'category': expense.category, 'recurrence_flag': expense.recurrence_flag}), 201


@bp.route('/expenses', methods=['GET'])
@jwt_required()
def list_expenses():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    category = request.args.get('category')

    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)

    # Convert date strings to datetime objects, handling potential errors
    start_date = None
    end_date = None

    # ... validation ...
    if start_date_str:
        if not validate_date_format(start_date_str):
            return jsonify({'error': 'Invalid start date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
        start_date = convert_to_iso(start_date_str)
    if end_date_str:
        if not validate_date_format(end_date_str):
            return jsonify({'error': 'Invalid end date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
        end_date = convert_to_iso(end_date_str)

    expenses = Expense.get_all_by_user_id(user.id, start_date, end_date, category)
    expenses_data = [{'id': e.id, 'user_id': e.user_id, 'amount': e.amount, 'description': e.description, 'date': e.date, 'category': e.category, 'recurrence_flag': e.recurrence_flag} for e in expenses]

    return jsonify(expenses_data), 200

@bp.route('/reports/expenses', methods=['GET'])
@jwt_required()
def total_expenses_per_category():
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    # Convert date strings to datetime objects, handling potential errors
    start_date = None
    end_date = None

    # ... validation ...
    if start_date_str:
        if not validate_date_format(start_date_str):
            return jsonify({'error': 'Invalid start date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
        start_date = convert_to_iso(start_date_str)
    if end_date_str:
        if not validate_date_format(end_date_str):
            return jsonify({'error': 'Invalid end date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
        end_date = convert_to_iso(end_date_str)

    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)

    expenses = Expense.get_all_by_user_id(user.id, start_date, end_date)

    totals = {}
    for expense in expenses:
        if expense.category in totals:
            totals[expense.category] += expense.amount
        else:
            totals[expense.category] = expense.amount

    return jsonify(totals), 200

@bp.route('/expenses/<int:expense_id>', methods=['GET'])
@jwt_required()
def get_expense(expense_id):
    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)
    expense = Expense.get_by_id(expense_id)

    if not expense or expense.user_id != user.id:
        return jsonify({'error': 'Expense not found or not authorized'}), 204

    return jsonify({'id': expense.id, 'user_id': expense.user_id, 'amount': expense.amount, 'description': expense.description, 'date': expense.date, 'category': expense.category}), 200

@bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@jwt_required()
def update_expense(expense_id):
    data = request.get_json()
    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)
    expense = Expense.get_by_id(expense_id)

    if not expense or expense.user_id != user.id:
        return jsonify({'error': 'Expense not found or not authorized'}), 204

    # Update fields (with validation)
    if 'amount' in data:
        if not isinstance(data['amount'], (int, float)):
            return jsonify({'error': 'Amount must be a number'}), 400
        expense.amount = data['amount']
    if 'description' in data:
        if not isinstance(data['description'], str):
            return jsonify({'error': 'Description must be a string'}), 400
        expense.description = data['description']
    if 'date' in data:
        if not isinstance(data['date'], str):
            return jsonify({'error': 'Date must be a string'}), 400
        if not validate_date_format(data['date']):
            return jsonify({'error': 'Invalid date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
        expense.date = data['date']
    if 'category' in data:
        if not isinstance(data['category'], str):
            return jsonify({'error': 'Category must be a string'}), 400
        expense.category = data['category']
    if 'recurrence_flag' in data:
        if not isinstance(data['recurrence_flag'], str):
            return jsonify({'error': 'Recurrence flag must be a string'}), 400
        if not validate_recurrence_flag(data['recurrence_flag']):
            return jsonify({'error': 'Invalid recurrence flag'}), 400
    expense.save()
    return jsonify({'id': expense.id, 'user_id': expense.user_id, 'amount': expense.amount, 'description': expense.description, 'date': expense.date, 'category': expense.category, 'recurrence_flag': expense.recurrence_flag}), 200

@bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@jwt_required()
def delete_expense(expense_id):
    current_username = get_jwt_identity()
    user = User.get_by_username(current_username)
    expense = Expense.get_by_id(expense_id)
    if not expense or expense.user_id != user.id:
        return jsonify({'error': 'Expense not found or not authorized'}), 204
    expense.delete()
    return jsonify({}), 204