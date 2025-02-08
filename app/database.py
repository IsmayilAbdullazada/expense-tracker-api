import sqlite3
from flask import g, current_app

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # Access DATABASE_URL through current_app.config:
        db_url = current_app.config['DATABASE_URL']
        db = g._database = sqlite3.connect(db_url)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db(app):
    with app.app_context():
        db = get_db()
        with app.open_resource('../schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

        # # --- Check if tables exist ---
        # cur = db.cursor()
        # cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        # user_table_exists = cur.fetchone() is not None

        # cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses';")
        # expenses_table_exists = cur.fetchone() is not None

        # if user_table_exists and expenses_table_exists:
        #     print("Tables created successfully!")
        # else:
        #     print("Error: Tables were not created correctly.")
        #     if not user_table_exists:
        #         print("  - users table is missing")
        #     if not expenses_table_exists:
        #         print("  - expenses table is missing")
        #     # Consider raising an exception here to halt execution
        #     # raise Exception("Database initialization failed.")

    app.teardown_appcontext(close_db)