import sqlite3 as sq
from flask import Flask
from flask import render_template   
app = Flask(__name__)
conn = sq.connect('db.sqlite3')

with open('db.sql') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()

@app.route('/')
def index():
    return 'Hello, World!'