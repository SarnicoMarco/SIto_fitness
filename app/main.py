from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def saluto():
    nome = "Marco"  # Sostituisci "Marco" con il nome che desideri visualizzare
    return render_template('home.html', nome=nome)

if __name__ == '__main__':
    app.run(debug=True)
