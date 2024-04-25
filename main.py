import sqlite3 as sq
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
import uuid


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
        cur.execute("SELECT password_hash FROM Account WHERE ID_account=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password(user[0], password):
            session['username'] = username
            return redirect(url_for('home'))  # Corretto il nome della funzione a cui reindirizzare
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ID_account = generate_id()  # Generate ID for the account
        password = request.form['password']
        ID_utente = generate_id()  # Generate ID for the user
        nomeutente = request.form['nomeutente']
        email = request.form['email']
        nome = request.form['nome']
        cognome = request.form['cognome']

        # Hash the password
        password_hash = hash_password(password)

        # Check if email and nomeutente already exist in the database
        conn = sq.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("SELECT * FROM Utente WHERE email=? ", (email,))
        cur.execute("SELECT * FROM Account WHERE nomeutente=?", (nomeutente,))
        existing_user = cur.fetchone()

        if existing_user:
            conn.close()
            return 'Email or nomeutente already exists'

        # Insert data into Account table
        cur.execute("INSERT INTO Account (ID_account, password_hash, ID_utente, nomeutente) VALUES (?, ?, ?, ?)", 
                    (ID_account, password_hash, ID_utente, nomeutente))
        
        # Insert data into Utente table
        cur.execute("INSERT INTO Utente (ID_utente, nome, cognome, email) VALUES (?, ?, ?, ?)", 
                    (ID_utente, nome, cognome, email))
        conn.commit()
        conn.close()

        # Redirect to index page after successful registration
        return redirect(url_for('index'))

    return render_template('register.html')

def generate_id():
    unique_id = str(uuid.uuid4())
    return unique_id





if __name__ == '__main__':
    app.run(debug=True)
