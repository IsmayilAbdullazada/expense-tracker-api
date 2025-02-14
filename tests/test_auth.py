import json

def test_register_user_success(register_user):
    response = register_user('testuser', 'testpass')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User registered successfully'

def test_register_duplicate_user(register_user):
    register_user('testuser', 'testpass')
    response = register_user('testuser', 'testpass')
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data

def test_register_missing_fields(client):
    response = client.post('/users/register', 
                         json={'username': 'testuser'})
    assert response.status_code == 400

def test_login_success(register_user, login_user):
    register_user('testuser', 'testpass')
    response = login_user('testuser', 'testpass')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data

def test_login_invalid_password(register_user, login_user):
    register_user('testuser', 'testpass')
    response = login_user('testuser', 'wrongpass')
    assert response.status_code == 401

def test_login_nonexistent_user(login_user):
    response = login_user('nonexistent', 'testpass')
    assert response.status_code == 401

# tests/test_auth.py
import json
import pytest

def test_register_user_success(client, register_user):
    response = register_user('newuser', 'newpassword')
    assert response.status_code == 201
    data = json.loads(response.get_data(as_text=True))
    assert data['message'] == 'User registered successfully'

def test_register_user_duplicate(client, register_user):
    register_user('existinguser', 'password')  # Register a user first
    response = register_user('existinguser', 'anotherpassword')
    assert response.status_code == 409
    data = json.loads(response.get_data(as_text=True))
    assert data['error'] == 'Username already exists'

def test_register_user_missing_fields(client):
    response = client.post('/users/register',
                           data=json.dumps({'username': 'onlyuser'}),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert "Missing username or password" in data['error'] #more precise assert

    response = client.post('/users/register',
                           data=json.dumps({'password': 'onlypassword'}),
                           content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert "Missing username or password" in data['error']

def test_login_success(client, register_user, login_user):
    register_user('loguser', 'logpassword')
    response = login_user('loguser', 'logpassword')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert 'access_token' in data

def test_login_wrong_credentials(client, register_user, login_user):
    register_user('loguser', 'logpassword')
    response = login_user('loguser', 'wrong_password')
    assert response.status_code == 401
    data = json.loads(response.get_data(as_text=True))
    assert 'Invalid credentials' in data['error']

    response = login_user('wrong_user', 'logpassword')
    assert response.status_code == 401
    data = json.loads(response.get_data(as_text=True))
    assert 'Invalid credentials' in data['error']

def test_login_missing_fields(client):
    response = client.post('/users/login', data=json.dumps({'username': 'onlyuser'}), content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert "Missing username or password" in data['error']

    response = client.post('/users/login', data=json.dumps({'password': 'onlypassword'}), content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.get_data(as_text=True))
    assert "Missing username or password" in data['error']