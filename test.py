import sqlite3
import datetime

db = sqlite3.connect('todo.db')
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tasks '
          '(id INTEGER PRIMARY KEY AUTOINCREMENT,'
          'task TEXT NOT NULL,'
          'completed NUMERIC NOT NULL,'
          'reg_date TEXT NOT NULL)')

values = ('할 일 테스트', datetime.datetime.now())
c.execute("INSERT INTO tasks (task, completed, reg_date) VALUES (?, False, ?)", values)
db.commit()

c.execute('SELECT id, task, completed, reg_date FROM tasks')
res = c.fetchall()
print(res)