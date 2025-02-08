import pytest
from app.models import User, Expense
from app.database import get_db, init_db, close_db
from app import create_app
from config import DevelopmentConfig, TestingConfig
from datetime import datetime

@pytest.fixture
def app():
    app = create_app(DevelopmentConfig)
    with app.app_context():
      init_db(app)
      yield app

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

def test_user_creation_and_retrieval(db, clean_db):  # Use clean_db
    user = User(username='testuser', password_hash='hashed_password')
    user.save()
    assert user.id is not None

    retrieved_user = User.get_by_username('testuser')
    assert retrieved_user is not None
    assert retrieved_user.username == 'testuser'
    assert retrieved_user.password_hash == 'hashed_password'

    retrieved_user_by_id = User.get_by_id(user.id)
    assert retrieved_user_by_id is not None
    assert retrieved_user_by_id.username == 'testuser'

    retrieved_non_existent_user = User.get_by_username('nonexistent')
    assert retrieved_non_existent_user is None

def test_user_password(db, clean_db):  # Use clean_db
    user = User(username="testPass", password_hash=None)
    user.set_password("test_password")
    assert user.check_password("test_password") is True
    assert user.check_password("wrong_password") is False
    user.save()

def test_expense_creation_retrieval_and_deletion(db, clean_db):  # Use clean_db
    user = User(username='expenseuser', password_hash='hashed')
    user.save()
    expense = Expense(user_id=user.id, amount=100.0, description='Test Expense', date='2024-07-27', category='Test')
    expense.save()
    assert expense.id is not None

    retrieved_expense = Expense.get_by_id(expense.id)
    assert retrieved_expense is not None
    assert retrieved_expense.amount == 100.0

    retrieved_non_existent_expense = Expense.get_by_id(999)
    assert retrieved_non_existent_expense is None

    # Test get_all_by_user_id
    expenses = Expense.get_all_by_user_id(user.id)
    assert len(expenses) == 1
    assert expenses[0].id == expense.id

    #test filtering by dates and category
    expenses = Expense.get_all_by_user_id(user.id, start_date='2024-07-26', end_date='2024-07-28', category="Test")
    assert len(expenses) == 1

    expenses = Expense.get_all_by_user_id(user.id, start_date='2025-07-26', end_date='2025-07-28', category="Test")
    assert len(expenses) == 0

    expenses = Expense.get_all_by_user_id(user.id, start_date='2024-07-26', end_date='2024-07-28', category="Food")
    assert len(expenses) == 0

    expense.delete()
    retrieved_expense_after_delete = Expense.get_by_id(expense.id)
    assert retrieved_expense_after_delete is None

def test_expense_update(db, clean_db):  # Use clean_db
    user = User(username='updateuser', password_hash='hashed')
    user.save()
    expense = Expense(user_id=user.id, amount=100.0, description='Test Expense', date='2024-07-27', category='Test')
    expense.save()
    expense.amount = 150.0
    expense.save()
    retrieved_expense = Expense.get_by_id(expense.id)
    assert retrieved_expense.amount == 150.0

# Removed since the validation method is already being tested.
# def test_validate_date_format():
#     from app.utils import validate_date_format
#     assert validate_date_format('2024-01-01T12:00:00Z') is True
#     assert validate_date_format('2024-01-01T12:00:00+00:00') is True
#     assert validate_date_format('2024-01-01') is False  # Missing time
#     assert validate_date_format('2024/01/01 12:00:00') is False  # Invalid separators
#     assert validate_date_format('invalid-date') is False
#     assert validate_date_format('2024-13-01T12:00:00Z') is False  # Invalid month