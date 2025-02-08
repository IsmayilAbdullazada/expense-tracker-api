import pytest
import json
from app import create_app
from app.database import init_db, get_db
from config import DevelopmentConfig
from app.models import User

@pytest.fixture
def app():
    app = create_app(DevelopmentConfig)
    with app.app_context():
        init_db(app)
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db(app):
    db = get_db()
    yield db

@pytest.fixture
def clean_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('../schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@pytest.fixture  # Changed: returns a *function* to register
def register_user(client):
    def _register_user(username, password):
        return client.post('/users/register',
                               data=json.dumps({'username': username, 'password': password}),
                               content_type='application/json')
    return _register_user

@pytest.fixture
def login_user(client):
    def _login_user(username, password):
        return client.post('/users/login',
                               data=json.dumps({'username': username, 'password': password}),
                               content_type='application/json')
    return _login_user

@pytest.fixture # token fixture now depends on login_user, no need for registered_user
def token(client, clean_db, login_user):
# Register the user directly within the token fixture (most robust approach)
    response = client.post('/users/register',
    data=json.dumps({'username': 'testuser', 'password': 'testpassword'}),
    content_type='application/json')
    assert response.status_code == 201  # Assert registration success

    # Now log in the user
    response = login_user('testuser', 'testpassword')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    return data['access_token']

def test_register_user(client, clean_db, register_user):  # Use clean_db and register_user
    response = register_user('newuser', 'newpassword') # Register a new user
    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))
    assert data['message'] == 'User registered successfully'

    # Test duplicate registration
    response = register_user('newuser', 'anotherpassword') # Register the same user
    assert response.status_code == 409
    data = json.loads(response.get_data(as_text=True))
    assert data['error'] == 'Username already exists'

    # Test missing fields
    response = client.post('/users/register',
                           data=json.dumps({'username': 'onlyuser'}),
                           content_type='application/json')
    assert response.status_code == 400

def test_login(client, clean_db, register_user, login_user): # Use clean_db, register_user, login_user
    register_user('loguser', 'logpassword')
    response = login_user('loguser', 'logpassword')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert 'access_token' in data

    # test wrong credentials
    response = login_user('loguser', 'wrong_password')
    assert response.status_code == 401

    response = login_user('wrong_user', 'logpassword')
    assert response.status_code == 401

    #test missing fields
    response = client.post('/users/login', data=json.dumps({'username': 'onlyuser'}), content_type='application/json')
    assert response.status_code == 400

def test_create_expense(client, token, clean_db, register_user):  # Use clean_db
    register_user('testuser', 'testpassword') # Register the user
    headers = {'Authorization': f'Bearer {token}'}

    # Test valid expense creation
    expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    assert response.status_code == 201
    created_expense = json.loads(response.get_data(as_text=True))
    assert created_expense['amount'] == 50.0
    assert created_expense['description'] == 'Groceries'
    assert created_expense['category'] == 'Food'
    assert created_expense['id'] is not None

    #Test missing fields
    expense_data = {'amount': 50.0,  'date': '2024-07-28T14:30:00Z', 'category': 'Food'} # Missing description
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    assert response.status_code == 400

    #Test invalid amount
    expense_data = {'amount': "abc", 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    assert response.status_code == 400

    # #Test invalid date
    # expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28', 'category': 'Food'}
    # response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    # assert response.status_code == 400

    # Test without token
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json')
    assert response.status_code == 401 # Unauthorized

def test_list_expenses(client, token, clean_db, register_user):  # Use clean_db
    register_user('testuser', 'testpassword')  # Register a test user.
    headers = {'Authorization': f'Bearer {token}'}
    expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    assert response.status_code == 201

    # Test without query parameters
    response = client.get('/expenses', headers=headers)
    assert response.status_code == 200
    retrieved_expenses = json.loads(response.get_data(as_text=True))
    assert len(retrieved_expenses) == 1

    # Test with start_date
    response = client.get('/expenses?start_date=2024-07-27T00:00:00Z', headers=headers)
    assert response.status_code == 200
    retrieved_expenses = json.loads(response.get_data(as_text=True))
    assert len(retrieved_expenses) == 1

    # Test with end_date
    response = client.get('/expenses?end_date=2024-07-29T00:00:00Z', headers=headers)
    assert response.status_code == 200
    retrieved_expenses = json.loads(response.get_data(as_text=True))
    assert len(retrieved_expenses) == 1

    # Test with category
    response = client.get('/expenses?category=Food', headers=headers)
    assert response.status_code == 200
    retrieved_expenses = json.loads(response.get_data(as_text=True))
    assert len(retrieved_expenses) == 1

    # Test with invalid date
    response = client.get('/expenses?start_date=invalid', headers=headers)
    assert response.status_code == 400

    # Test without token
    response = client.get('/expenses')
    assert response.status_code == 401  # Unauthorized

def test_get_expense(client, token, clean_db, register_user):  # Use clean_db
    register_user('testuser', 'testpassword')  # Register a test user.
    headers = {'Authorization': f'Bearer {token}'}
    expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    assert response.status_code == 201
    expense_id = json.loads(response.get_data(as_text=True))['id']
    response = client.get(f'/expenses/{expense_id}', headers=headers)
    assert response.status_code == 200
    retrieved_expense = json.loads(response.get_data(as_text=True))
    assert retrieved_expense['id'] == expense_id

    #Test unauthorized
    response = client.get(f'/expenses/{expense_id}') # Missing token
    assert response.status_code == 401  # Unauthorized

    #Test not found / unauthorized
    response = client.get(f'/expenses/9999', headers=headers)
    assert response.status_code == 204

def test_update_expense(client, token, clean_db, register_user):  # Use clean_db
    register_user('testuser', 'testpassword')  # Register a test user.
    headers = {'Authorization': f'Bearer {token}'}
    expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    expense_id = json.loads(response.get_data(as_text=True))['id']

    # Test valid update
    updated_data = {'amount': 75.0, 'description': 'Updated Groceries'}
    response = client.put(f'/expenses/{expense_id}', data=json.dumps(updated_data), content_type='application/json', headers=headers)
    assert response.status_code == 200
    updated_expense = json.loads(response.get_data(as_text=True))
    assert updated_expense['amount'] == 75.0
    assert updated_expense['description'] == 'Updated Groceries'

    # Test invalid data
    response = client.put(f'/expenses/{expense_id}', data=json.dumps({'amount': 'invalid'}), content_type='application/json', headers=headers)
    assert response.status_code == 400

    # Test expense not found
    response = client.put('/expenses/999', data=json.dumps(updated_data), content_type='application/json', headers=headers)  # Non-existent ID
    assert response.status_code == 204

    #Test unauthorized
    response = client.put(f'/expenses/{expense_id}', data=json.dumps(updated_data), content_type='application/json')  # Missing token
    assert response.status_code == 401

def test_delete_expense(client, token, clean_db, register_user):  # Use clean_db
    register_user('testuser', 'testpassword')  # Register a test user.
    headers = {'Authorization': f'Bearer {token}'}
    expense_data = {'amount': 50.0, 'description': 'Groceries', 'date': '2024-07-28T14:30:00Z', 'category': 'Food'}
    response = client.post('/expenses', data=json.dumps(expense_data), content_type='application/json', headers=headers)
    expense_id = json.loads(response.get_data(as_text=True))['id']

    # Test valid delete
    response = client.delete(f'/expenses/{expense_id}', headers=headers)
    assert response.status_code == 204

    # Test expense not found
    response = client.delete(f'/expenses/{expense_id}', headers=headers)  # Already deleted
    assert response.status_code == 204

    #Test unauthorized
    response = client.delete(f'/expenses/{expense_id}')
    assert response.status_code == 401