import json
from datetime import datetime, timedelta, timezone

# Helper function for creating expenses
def create_expense(client, token, amount=100, description="Test Expense",
                   date="2024-07-28T14:30:00Z", category="Test"):
    headers = {'Authorization': f'Bearer {token}'}
    expense_data = {
        'amount': amount,
        'description': description,
        'date': date,
        'category': category
    }
    return client.post('/expenses', data=json.dumps(expense_data),
                       content_type='application/json', headers=headers)

def test_create_expense_valid(client, token):
    response = create_expense(client, token)
    assert response.status_code == 201
    created_expense = json.loads(response.get_data(as_text=True))
    assert created_expense['amount'] == 100
    assert created_expense['description'] == 'Test Expense'
    assert created_expense['date'] == '2024-07-28T14:30:00+00:00'
    assert created_expense['category'] == 'Test'
    assert created_expense['id'] is not None

def test_create_expense_missing_fields(client, token):
    # Missing description
    response = create_expense(client, token, description=None)
    assert response.status_code == 400

    # Missing amount
    response = create_expense(client, token, amount=None)
    assert response.status_code == 400

    # Missing date
    response = create_expense(client, token, date=None)
    assert response.status_code == 400

    # Missing category
    response = create_expense(client, token, category=None)
    assert response.status_code == 400

def test_create_expense_invalid_amount(client, token):
    response = create_expense(client, token, amount="invalid")
    assert response.status_code == 400

def test_create_expense_invalid_date(client, token):
    response = create_expense(client, token, date="invalid-date")
    assert response.status_code == 400

def test_create_expense_unauthorized(client):
    response = client.post('/expenses', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 401

def test_list_expenses_no_filters(client, token):
    create_expense(client, token)  # Create at least one expense
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/expenses', headers=headers)
    assert response.status_code == 200
    expenses = json.loads(response.get_data(as_text=True))
    assert len(expenses) > 0 # Check that the list is not empty

def test_list_expenses_filter_by_start_date(client, token):
    today = datetime.now(timezone.utc).date().isoformat()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat()
    create_expense(client, token, date=today)
    create_expense(client, token, date=yesterday)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'/expenses?start_date={yesterday}', headers=headers)
    assert response.status_code == 200
    expenses = json.loads(response.get_data(as_text=True))
    assert len(expenses) == 2

    response = client.get(f'/expenses?start_date={today}', headers=headers)
    assert response.status_code == 200
    expenses = json.loads(response.get_data(as_text=True))
    assert len(expenses) == 1

def test_list_expenses_filter_by_end_date(client, token):
    today = datetime.now(timezone.utc).date().isoformat()
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat()
    create_expense(client, token, date=today)

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'/expenses?end_date={tomorrow}', headers=headers)
    assert response.status_code == 200
    expenses = json.loads(response.get_data(as_text=True))
    assert len(expenses) == 1

def test_list_expenses_filter_by_category(client, token):
    create_expense(client, token, category="Food")
    create_expense(client, token, category="Travel")

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/expenses?category=Food', headers=headers)
    assert response.status_code == 200
    expenses = json.loads(response.get_data(as_text=True))
    assert len(expenses) == 1
    assert expenses[0]['category'] == 'Food'

def test_list_expenses_invalid_date_filter(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/expenses?start_date=invalid', headers=headers)
    assert response.status_code == 400

def test_list_expenses_unauthorized(client):
    response = client.get('/expenses')
    assert response.status_code == 401

def test_get_expense_valid(client, token):
    response = create_expense(client, token)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get(f'/expenses/{expense_id}', headers=headers)
    assert response.status_code == 200
    retrieved_expense = json.loads(response.get_data(as_text=True))
    assert retrieved_expense['id'] == expense_id

def test_get_expense_not_found(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/expenses/9999', headers=headers)
    assert response.status_code == 204

def test_get_expense_unauthorized(client):
    response = client.get('/expenses/1')
    assert response.status_code == 401

def test_update_expense_valid(client, token):
    response = create_expense(client, token)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers = {'Authorization': f'Bearer {token}'}
    updated_data = {'amount': 150, 'description': 'Updated Expense'}
    response = client.put(f'/expenses/{expense_id}', data=json.dumps(updated_data),
                          content_type='application/json', headers=headers)
    assert response.status_code == 200
    updated_expense = json.loads(response.get_data(as_text=True))
    assert updated_expense['amount'] == 150
    assert updated_expense['description'] == 'Updated Expense'

def test_update_expense_partial(client, token):
    response = create_expense(client, token)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers = {'Authorization': f'Bearer {token}'}
     # Update only the description
    updated_data = {'description': 'New Description'}
    response = client.put(f'/expenses/{expense_id}', data=json.dumps(updated_data),
                         content_type='application/json', headers=headers)
    assert response.status_code == 200
    updated_expense = json.loads(response.get_data(as_text=True))
    # Check updated field
    assert updated_expense['description'] == 'New Description'
    # Check unchanged fields
    assert updated_expense['amount'] == 100
    assert updated_expense['date'] == '2024-07-28T14:30:00+00:00'
    assert updated_expense['category'] == 'Test'

def test_update_expense_invalid_data(client, token):
    response = create_expense(client, token)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put(f'/expenses/{expense_id}', data=json.dumps({'amount': 'invalid'}),
                          content_type='application/json', headers=headers)
    assert response.status_code == 400

def test_update_expense_not_found(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.put('/expenses/9999', data=json.dumps({}), content_type='application/json', headers=headers)
    assert response.status_code == 204

def test_update_expense_unauthorized(client):
    response = client.put('/expenses/1', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 401

def test_delete_expense_valid(client, token):
    response = create_expense(client, token)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete(f'/expenses/{expense_id}', headers=headers)
    assert response.status_code == 204
    # Verify deletion
    response = client.get(f'/expenses/{expense_id}', headers=headers)
    assert response.status_code == 204

def test_delete_expense_not_found(client, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = client.delete('/expenses/9999', headers=headers)
    assert response.status_code == 204

def test_delete_expense_unauthorized(client):
    response = client.delete('/expenses/1')
    assert response.status_code == 401

def test_expense_cross_user_access(client, token, register_user, login_user):
    # Create expense for user 1
    register_user('user1', 'password')
    login_response1 = login_user('user1', 'password')
    token1 = json.loads(login_response1.get_data(as_text=True))['access_token']
    response = create_expense(client, token1)
    expense_id = json.loads(response.get_data(as_text=True))['id']
    headers1 = {'Authorization': f'Bearer {token1}'}

    # Register and login user 2
    register_user('user2', 'password2')
    login_response2 = login_user('user2', 'password2')
    token2 = json.loads(login_response2.get_data(as_text=True))['access_token']
    headers2 = {'Authorization': f'Bearer {token2}'}

    # User 2 attempts to get user 1's expense
    response = client.get(f'/expenses/{expense_id}', headers=headers2)
    assert response.status_code == 204

    # User 2 attempts to update user 1's expense
    response = client.put(f'/expenses/{expense_id}', data=json.dumps({}),
                          content_type='application/json', headers=headers2)
    assert response.status_code == 204

    # User 2 attempts to delete user 1's expense
    response = client.delete(f'/expenses/{expense_id}', headers=headers2)
    assert response.status_code == 204