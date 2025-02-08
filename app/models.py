from .database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

class User:
  def __init__(self, username, password_hash, id=None):
    self.id = id
    self.username = username
    self.password_hash = password_hash

  def save(self):
    db = get_db()
    if self.id is None:
      cur = db.execute('INSERT INTO users (username, password_hash) VALUES (?,?)', (self.username, self.password_hash))
      db.commit()
      self.id = cur.lastrowid # Update id after insertion.
    else:
      db.execute('UPDATE users SET username = ?, password_hash = ? WHERE id = ?', (self.username, self.password_hash, self.id))
      db.commit()
    return self

  @staticmethod
  def get_by_username(username):
      db = get_db()
      cur = db.execute('SELECT * FROM users WHERE username = ?', (username,))
      row = cur.fetchone()
      if row:
          return User(id=row['id'], username=row['username'], password_hash=row['password_hash'])
      return None

  @staticmethod
  def get_by_id(user_id):
      db = get_db()
      cur = db.execute('SELECT * FROM users WHERE id = ?', (user_id,))
      row = cur.fetchone()
      if row:
          return User(id=row['id'], username=row['username'], password_hash=row['password_hash'])
      return None
  def set_password(self, password):
      self.password_hash = generate_password_hash(password)

  def check_password(self, password):
      return check_password_hash(self.password_hash, password)

class Expense:
  def __init__(self, user_id, amount, description, date, category, id=None ):
    self.id = id
    self.user_id = user_id
    self.amount = amount
    self.description = description
    self.date = date
    self.category = category

  def save(self):
    db = get_db()
    if self.id is None:
      cur = db.execute('''INSERT INTO expenses (user_id, amount, description, date, category)
                        VALUES (?,?,?,?,?)''', (self.user_id, self.amount, self.description, self.date, self.category))
      db.commit()
      self.id = cur.lastrowid
    else:
      db.execute('''UPDATE expenses SET user_id =?, amount = ?, description = ?, date = ?, category =?
                  WHERE id = ?''', (self.user_id, self.amount, self.description, self.date, self.category, self.id))
      db.commit()
    return self

  @staticmethod
  def get_by_id(expense_id):
      db = get_db()
      cur = db.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,))
      row = cur.fetchone()
      if row:
          return Expense(user_id = row['user_id'], amount = row['amount'], description = row['description'], date = row['date'], category = row['category'], id = row['id'])
      return None

  @staticmethod
  def get_all_by_user_id(user_id, start_date=None, end_date=None, category=None):
      db = get_db()
      query = 'SELECT * FROM expenses WHERE user_id = ?'
      params = [user_id]
      if start_date:
          query += ' AND date >= ?'
          params.append(start_date)
      if end_date:
          query += ' AND date <= ?'
          params.append(end_date)
      if category:
          query += ' AND category = ?'
          params.append(category)
      query += ' ORDER BY date DESC'  # Example: Order by date
      cur = db.execute(query, params)
      expenses = []

      for row in cur.fetchall():
        expenses.append(Expense(user_id = row['user_id'], amount = row['amount'], description = row['description'], date = row['date'], category = row['category'], id = row['id']))
      return expenses

  def delete(self):
    db = get_db()
    db.execute('DELETE FROM expenses WHERE id = ?', (self.id,))
    db.commit()