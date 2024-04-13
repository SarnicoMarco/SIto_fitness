import sqlite3 as sq
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
app.secret_key = 'your_secret_key'


conn = sq.connect('db.sqlite3')

# Create the tables
with open('db.sql') as f:
    conn.executescript(f.read())
conn.commit()
conn.close()

# Funzioni per l'hashing delle password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(hashed_password, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

#Render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        conn = sq.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT * FROM Account WHERE ID_account=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password(user[1], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ID_account = request.form['ID_account']
        password = request.form['password']
        ID_utente = request.form['ID_utente']
        nomeutente = request.form['nomeutente']

        password_hash = hash_password(password)

        conn = sq.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("INSERT INTO Account (ID_account, password_hash, ID_utente, nomeutente) VALUES (?, ?, ?, ?)", 
                    (ID_account, password_hash, ID_utente, nomeutente))
        conn.commit()
        conn.close()

        return 'Account registered successfully'

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
