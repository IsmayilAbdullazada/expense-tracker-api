# Flask Expense Tracker API

A simple REST API for managing user expenses, built with Flask, SQLite, and JWT authentication.

## Table of Contents

1.  [Project Structure](#project-structure)
2.  [Prerequisites](#prerequisites)
3.  [Setup](#setup)
    - [Clone the Repository](#clone-the-repository)
    - [Create a Virtual Environment](#create-a-virtual-environment)
    - [Install Dependencies](#install-dependencies)
    - [Environment Variables](#environment-variables)
4.  [Database Setup](#database-setup)
    - [Schema](#schema)
5.  [Running the Application](#running-the-application)
    - [Development Mode](#development-mode)
6.  [Testing](#testing)
7.  [API Endpoints](#api-endpoints)
8.  [Contributing](#contributing)
9.  [License](#license)

## 1. Project Structure

```
flask-expense-tracker/       <-- Project root directory
├── app/
│   ├── __init__.py          <-- Flask application initialization
│   ├── database.py         <-- Database connection and initialization
│   ├── models.py           <-- User and Expense models
│   ├── routes.py           <-- API endpoints
│   └── utils.py            <-- Utility functions (date validation)
├── tests/                  <-- Unit and integration tests
│   ├── __init__.py
│   ├── test_app.py         <-- Integration tests for API endpoints
│   └── test_models.py      <-- Unit tests for models
├── .env                    <-- Environment variables (DO NOT COMMIT)
├── .gitignore              <-- Files and directories to ignore in Git
├── config.py               <-- Configuration settings
├── requirements.txt        <-- Project dependencies
├── run.py                  <-- Application entry point
└── schema.sql              <-- Database schema
```

## 2. Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 3. Setup

### Clone the Repository

```bash
git clone https://github.com/IsmayilAbdullazada/expense-tracker-api.git
cd expense-tracker-api
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

- **Linux/macOS:**

  ```bash
  source venv/bin/activate
  ```

- **Windows:**

  ```bash
  venv\Scripts\activate
  ```

You should see `(venv)` at the beginning of your terminal prompt.

### Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project's root directory and add the following:

```
FLASK_ENV=development
DATABASE_URL=expenses.db
SECRET_KEY=<your_secret_key>
JWT_SECRET_KEY=<your_jwt_secret_key>
```

- **`FLASK_ENV`:** Set to `development`, `testing`, or `production`.
- **`DATABASE_URL`:** The path to your SQLite database file (for development).
- **`SECRET_KEY` and `JWT_SECRET_KEY`:** You can generate them using the provided `key_generator.py` script:

  ```bash
  python key_generator.py
  ```

  Copy the generated keys into your `.env` file

## 4. Database Setup

### Schema

The database schema is defined in `schema.sql`. The application automatically creates the database tables.

## 5. Running the Application

### Development Mode

```bash
python run.py
```

This will start the Flask development server (usually on `http://127.0.0.1:5000`). The database will be persistent on each restart

## 6. Testing

```bash
python -m pytest
```

This command runs all tests in the `tests` directory using the `pytest` framework. The tests use an in-memory SQLite database.

## 7. API Endpoints

All API endpoints require JWT authentication (except for user registration and login). Obtain a JWT by logging in. Include the token in the `Authorization` header of your requests:

```
Authorization: Bearer <your_jwt_token>
```

| Method   | URL                          | Description                | Request Body                                                                                        | Response (Success)                                           | Response (Error)                                                               |
| :------- | :--------------------------- | :------------------------- | :-------------------------------------------------------------------------------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------------------------- |
| `POST`   | `/users/register`            | Register a new user        | `{"username": "<username>", "password": "<password>"}`                                              | `201 Created`: `{"message": "User registered successfully"}` | `400 Bad Request`: Missing/invalid fields<br>`409 Conflict`: Username exists   |
| `POST`   | `/users/login`               | Log in an existing user    | `{"username": "<username>", "password": "<password>"}`                                              | `200 OK`: `{"access_token": "<your_jwt_token>"}`             | `400 Bad Request`: Missing fields <br> `401 Unauthorized`: Invalid credentials |
| `POST`   | `/expenses`                  | Create a new expense       | `{"amount": <amount>, "description": "<desc>", "date": "<date>", "category": "<category>"}`         | `201 Created`: Expense data (JSON)                           | `400 Bad Request`: Validation errors <br> `401 Unauthorized`                   |
| `GET`    | `/expenses`                  | List all expenses          | None (Optional: `start_date`, `end_date`, `category` as query parameters)                           | `200 OK`: Array of expense data (JSON)                       | `400 Bad Request`: Invalid date<br>`401 Unauthorized`                          |
| `GET`    | `/expenses/<int:expense_id>` | Get a specific expense     | None                                                                                                | `200 OK`: Expense data (JSON)                                | `404 Not Found` / `401 Unauthorized`                                           |
| `PUT`    | `/expenses/<int:expense_id>` | Update an existing expense | Any of: `{"amount": <amount>, "description": "<desc>", "date": "<date>", "category": "<category>"}` | `200 OK`: Updated expense data (JSON)                        | `400 Bad Request`: Validation errors <br> `404 Not Found` / `401 Unauthorized` |
| `DELETE` | `/expenses/<int:expense_id>` | Delete an expense          | None                                                                                                | `204 No Content`                                             | `404 Not Found` / `401 Unauthorized`                                           |

## Sample Request Body

### User - Register

```json
{
  "username": "testuser",
  "password": "testpassword"
}
```

### User - Login

```json
{
  "username": "testuser",
  "password": "testpassword"
}
```

### Expenses

```json
{
  "amount": 50.0,
  "description": "Groceries",
  "date": "2024-07-28T14:30:00Z",
  "category": "Food"
}
```

## 9. License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

```
