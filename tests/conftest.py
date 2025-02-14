import pytest
import json
from app import create_app
from app.database import init_db, get_db, close_db
from config import TestingConfig

@pytest.fixture(scope='session')
def app():
    """Create and configure the app for testing."""
    app = create_app(TestingConfig)
    with app.app_context():
        init_db(app)
        yield app

@pytest.fixture(scope='function', autouse=True)
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function', autouse=True)
def db(app):
    """Provides a database connection and handles setup/teardown."""
    with app.app_context():
        db = get_db()
        # Get the directory of the current file (conftest.py)
        with app.open_resource('../schema.sql', mode='r') as f:
          db.cursor().executescript(f.read())
        db.commit()

        yield db

        #Teardown:  Drop tables after each test
        db.cursor().execute("DROP TABLE IF EXISTS expenses")
        db.cursor().execute("DROP TABLE IF EXISTS users")
        db.commit()
        close_db() #close connection


@pytest.fixture
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

@pytest.fixture
def token(client, login_user, register_user):
    # Use the register_user fixture to create a user.
    register_response = register_user('testuser', 'testpassword')
    assert register_response.status_code == 201

    # Now log in the user
    response = login_user('testuser', 'testpassword')
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    return data['access_token']