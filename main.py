import sqlite3 as sq
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
import uuid
from flask import jsonify



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



    
@app.route('/aggiungi_PR', methods=['POST', 'GET'])
def aggiungi_PR():
    if request.method == 'POST':
        try:
            # Ottenere i dati dal modulo HTML
            esercizio = request.form['esercizio']
            peso = request.form['peso']
            account_id = session.get('account_id')  # Recupera l'ID dell'account dalla sessione
            
            conn = sq.connect('db.sqlite3')
            cur = conn.cursor()

            # Verifica se l'esercizio esiste già per quell'account
            cur.execute("SELECT * FROM PR WHERE esercizio=? AND ID_account=?", (esercizio, account_id))
            existing_pr = cur.fetchone()

            if existing_pr:
                # Se l'esercizio esiste già, esegui un aggiornamento
                cur.execute("UPDATE PR SET peso=? WHERE esercizio=? AND ID_account=?", (peso, esercizio, account_id))
            else:
                # Se l'esercizio non esiste, inseriscilo
                ID_pr = generate_id()
                cur.execute("INSERT INTO PR (ID_pr, esercizio, peso, ID_account) VALUES (?, ?, ?, ?)", 
                            (ID_pr, esercizio, peso, account_id))

            conn.commit()
            conn.close()
            return redirect(url_for('home'))
        except Exception as e:
            # Stampa l'errore per il debug
            print("Errore durante l'inserimento o l'aggiornamento del PR:", str(e))
            # Puoi anche registrare l'errore in un file di log o visualizzarlo nel browser per il debug
            return "Errore durante l'inserimento o l'aggiornamento del PR"
    return render_template('aggiungi_PR.html')



@app.route('/mostra_pr')
def mostra_pr():
    conn = sq.connect('db.sqlite3')
    cursor = conn.cursor()
    id_account = session.get('account_id')
    cursor.execute("SELECT * FROM PR WHERE ID_account = ?", (id_account,))
    pr_list = cursor.fetchall()

    return render_template('mostra_pr.html', pr_list=pr_list)


def get_pr_leaderboard():
    conn = sq.connect('db.sqlite3')
    cursor = conn.cursor()

    # Query per ottenere il PR massimo per ogni esercizio con il nome utente e il nickname
    cursor.execute("""
        SELECT PR.esercizio, PR.peso, Account.nomeutente
        FROM PR
        INNER JOIN Account ON PR.ID_account = Account.ID_account
        WHERE (PR.esercizio, PR.peso) IN (
            SELECT esercizio, MAX(peso)
            FROM PR
            GROUP BY esercizio
        )
    """)
    pr_leaderboard = cursor.fetchall()

    conn.close()
    return pr_leaderboard

@app.route('/classifica_pr')
def classifica_pr():
    # Ottieni i dati della classifica dei PR
    pr_leaderboard = get_pr_leaderboard()
    # Passa i dati alla pagina HTML utilizzando il metodo render_template
    return render_template('classifica_pr.html', pr_leaderboard=pr_leaderboard)



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



@app.route('/inserisci_allenamento', methods=['GET', 'POST'])
def inserisci_allenamento():
    conn = sq.connect('db.sqlite3')
    cursor = conn.cursor()
    if request.method == 'POST':
        # Recupera l'ID dell'account dalla sessione
        id_allenamento=generate_id()
        id_account = session.get('account_id')
        # Inserisci l'allenamento nel database
        obiettivo_allenamento = request.form['obiettivo_allenamento']
        num_schede = int(request.form['num_schede'])
        cursor.execute("INSERT INTO Allenamento (ID_allenamento, ID_account, obbiettivo_allenamento, num_schede) VALUES (?,?, ?, ?)",
                       (id_allenamento,id_account, obiettivo_allenamento, num_schede))
        conn.commit()

        # Ottieni l'ID dell'allenamento appena inserito
        id_allenamento = cursor.lastrowid

        # Inserisci le schede per l'allenamento
        for i in range(1, num_schede + 1):
            id_scheda=generate_id()
            tipo_scheda = request.form[f'tipo_scheda_{i}']
            cursor.execute("INSERT INTO Scheda (ID_scheda,tipo_scheda, ID_allenamento) VALUES (?, ?, ?)",
                           (id_scheda,tipo_scheda, id_allenamento))
            conn.commit()
            id_scheda = cursor.lastrowid

            # Inserisci gli esercizi per la scheda
            num_esercizi = int(request.form[f'num_esercizi_{i}'])
            for j in range(1, num_esercizi + 1):
                id_esercizio=generate_id()
                nome_esercizio = request.form[f'nome_esercizio_{i}_{j}']
                n_serie = request.form[f'n_serie_{i}_{j}']
                n_ripetizioni = request.form[f'n_ripetizioni_{i}_{j}']
                tempo_fase_concentrica = request.form[f'tempo_fase_concentrica_{i}_{j}']
                tempo_fase_eccentrica = request.form[f'tempo_fase_eccentrica_{i}_{j}']
                cursor.execute("INSERT INTO Esercizio (id_esercizio,nome_esercizio, ID_scheda, n_serie, n_ripetizioni, tempo_fase_concentrica, tempo_fase_eccentrica) VALUES (?,?, ?, ?, ?, ?, ?)",
                               (id_esercizio,nome_esercizio, id_scheda, n_serie, n_ripetizioni, tempo_fase_concentrica, tempo_fase_eccentrica))
                conn.commit()

        return redirect('home')  # Reindirizza alla dashboard dopo l'inserimento

    else:
        return render_template('inserisci_allenamento.html')


@app.route('/logout')
def logout():
    # Cancella tutte le variabili di sessione
    session.clear()
    # Reindirizza l'utente alla pagina di accesso
    return redirect(url_for('login'))

# Funzione per ottenere i dati dell'utente e dell'account dal database
def get_user_data():
    conn = sq.connect('db.sqlite3')
    cur = conn.cursor()

    # Ottieni i dati dell'utente e dell'account
    cur.execute("SELECT * FROM Utente INNER JOIN Account ON Utente.ID_utente = Account.ID_utente")
    user_data = cur.fetchone()

    conn.close()

    # Verifica se i dati sono stati recuperati correttamente
    if user_data:
        utente = {
            'ID_utente': user_data[0],
            'nome': user_data[1],
            'cognome': user_data[2],
            'email': user_data[3]
        }
        account = {
            'ID_account': user_data[4],
            'password_hash': user_data[5],
            'ID_utente': user_data[6],
            'nomeutente': user_data[7]
        }
        return utente, account
    else:
        return None, None

# Route per la pagina Utente
@app.route('/utente')
def utente():
    # Ottieni i dati dell'utente e dell'account dal database
    utente, account = get_user_data()
    
    # Se i dati non sono stati recuperati correttamente, restituisci una pagina di errore
    if not utente or not account:
        return render_template('errore.html', message="Errore nel recupero dei dati utente e account.")

    # Renderizza la pagina HTML con i dati dell'utente e dell'account
    return render_template('utente.html', utente=utente, account=account)

if __name__ == '__main__':
    app.run(debug=True)




