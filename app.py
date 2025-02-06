from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory data storage (replace with a database in a real application)
expenses = []
next_expense_id = 1  # Keep track of the next ID to assign


@app.route('/expenses', methods=['POST'])
def create_expense():
    global next_expense_id
    try:
        data = request.get_json()

        # Validate required fields (important for robust API)
        required_fields = ['amount', 'description', 'date', 'category']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields', 'required_fields': required_fields}), 400

        # Basic type validation (add more specific validation as needed)
        if not isinstance(data['amount'], (int, float)):
            return jsonify({'error': 'Amount must be a number'}), 400
        if not isinstance(data['description'], str):
            return jsonify({'error': 'Description must be a string'}), 400
        if not isinstance(data['date'], str):  # You might want more robust date validation
            return jsonify({'error': 'Date must be a string'}), 400
        if not isinstance(data['category'], str):
            return jsonify({'error': 'Category must be a string'}), 400
        #Date format validation
        from datetime import datetime
        try:
            datetime.fromisoformat(data['date'].replace('Z', '+00:00')) #Handles Z and +00:00
        except ValueError:
            return jsonify({'error': 'Invalid date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400


        expense = {
            'id': next_expense_id,
            'amount': data['amount'],
            'description': data['description'],
            'date': data['date'],
            'category': data['category']
        }
        expenses.append(expense)
        next_expense_id += 1
        return jsonify(expense), 201  # 201 Created

    except Exception as e:
        return jsonify({'error': 'Invalid JSON payload or server error', 'message': str(e)}), 400


@app.route('/expenses', methods=['GET'])
def list_expenses():
    return jsonify(expenses), 200


@app.route('/expenses/<int:expense_id>', methods=['GET'])
def get_expense(expense_id):
    for expense in expenses:
        if expense['id'] == expense_id:
            return jsonify(expense), 200
    return jsonify({'error': 'Expense not found'}), 404  # 404 Not Found


@app.route('/expenses/<int:expense_id>', methods=['PUT'])
def update_expense(expense_id):
    try:
        data = request.get_json()
        for i, expense in enumerate(expenses):
            if expense['id'] == expense_id:

              #Validate fields
              if 'amount' in data:
                if not isinstance(data['amount'], (int, float)):
                    return jsonify({'error': 'Amount must be a number'}), 400
                expenses[i]['amount'] = data['amount']
              if 'description' in data:
                if not isinstance(data['description'], str):
                    return jsonify({'error': 'Description must be a string'}), 400
                expenses[i]['description'] = data['description']
              if 'date' in data:
                if not isinstance(data['date'], str):  # You might want more robust date validation
                    return jsonify({'error': 'Date must be a string'}), 400
                 #Date format validation
                from datetime import datetime
                try:
                    datetime.fromisoformat(data['date'].replace('Z', '+00:00')) #Handles Z and +00:00
                except ValueError:
                    return jsonify({'error': 'Invalid date format.  Use ISO 8601 format (e.g., YYYY-MM-DDTHH:MM:SSZ).' }), 400
                expenses[i]['date'] = data['date']
              if 'category' in data:
                if not isinstance(data['category'], str):
                    return jsonify({'error': 'Category must be a string'}), 400
                expenses[i]['category'] = data['category']
              return jsonify(expenses[i]), 200  # 200 OK
        return jsonify({'error': 'Expense not found'}), 404

    except Exception as e:
        return jsonify({'error': 'Invalid JSON payload', 'message':str(e)}), 400


@app.route('/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    for i, expense in enumerate(expenses):
        if expense['id'] == expense_id:
            del expenses[i]
            return jsonify({}), 204  # 204 No Content
    return jsonify({'error': 'Expense not found'}), 404


if __name__ == '__main__':
    app.run(debug=True)  # Use debug=True for development only