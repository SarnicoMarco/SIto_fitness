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
        cur.execute("SELECT password_hash FROM Account WHERE nomeutente=?", (username,))
        user = cur.fetchone()
        conn.close()

        if user and check_password(user[0], password):
            session['username'] = username
            session['account_id'] = get_account_id(username)
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

        # Verifica se l'email esiste già
        cur.execute("SELECT * FROM Utente WHERE email=?", (email,))
        existing_email = cur.fetchone()
        if existing_email:
            conn.close()
            return 'Email already exists'

        # Verifica se il nome utente esiste già
        cur.execute("SELECT * FROM Account WHERE nomeutente=?", (nomeutente,))
        existing_username = cur.fetchone()
        if existing_username:
            conn.close()
            return 'Username already exists'

        # Se l'email e il nome utente non esistono già, procedi con l'inserimento dei dati
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


# Pagina iniziale per l'aggiunta del PR
@app.route('/aggiungi_pr', methods=['GET'])
def aggiungi_pr():
    return render_template('aggiungi_pr.html')

@app.route('/add_pr', methods=['POST'])
def add_pr():
    if request.method == 'POST':
        # Ottenere i dati dal modulo HTML
        ID_PR = generate_id()
        esercizio = request.form['esercizio']
        peso = request.form['peso']
        account_id = session.get('account_id')  # Recupera l'ID dell'account dalla sessione
        
        conn = sq.connect('db.sqlite3')
        cur = conn.cursor()
        cur.execute("INSERT INTO Utente (ID_account, esercizio, peso) VALUES (?, ?, ?)", 
                    (account_id, esercizio, peso))  # Aggiungi l'ID dell'account al PR
        conn.commit()
        conn.close()
        return redirect(url_for('home'))


def get_account_id(username):
    conn = sq.connect('db.sqlite3')
    cur = conn.cursor()
    cur.execute("SELECT ID_account FROM Account WHERE nomeutente=?", (username,))
    account_id = cur.fetchone()
    conn.close()
    if account_id:
        return account_id[0]  # Restituisce l'ID dell'account
    else:
        return None  # Se l'account non viene trovato, restituisce None




if __name__ == '__main__':
    app.run(debug=True)



