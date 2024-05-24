-- Creazione della tabella Utente
CREATE TABLE IF NOT EXISTS Utente (
    ID_utente INT PRIMARY KEY,
    nome VARCHAR(50),
    cognome VARCHAR(50),
    email VARCHAR(100)
);

-- Creazione della tabella Account
CREATE TABLE IF NOT EXISTS Account (
    ID_account INT PRIMARY KEY,
    password_hash VARCHAR(100),
    ID_gruppo INT,
    ID_utente INT,
    nomeutente VARCHAR(50),
    FOREIGN KEY (ID_utente) REFERENCES Utente(ID_utente)
);


-- Creazione della tabella PR (Personal Record)
CREATE TABLE IF NOT EXISTS PR (
    ID_pr INT PRIMARY KEY,
    esercizio VARCHAR(50),
    peso FLOAT,
    ID_account INT,
    FOREIGN KEY (ID_account) REFERENCES Account(ID_account)
);

-- Creazione della tabella Allenamento
CREATE TABLE IF NOT EXISTS Allenamento (
    ID_allenamento INT PRIMARY KEY,
    ID_account INT,
    obbiettivo_allenamento VARCHAR(50),
    num_schede INT,
    FOREIGN KEY (ID_account) REFERENCES Account(ID_account)
);

-- Creazione della tabella Scheda
CREATE TABLE IF NOT EXISTS Scheda (
    ID_scheda INT PRIMARY KEY,
    tipo_scheda VARCHAR(50),
    ID_allenamento INT,
    FOREIGN KEY (ID_allenamento) REFERENCES Allenamento(ID_allenamento)
);

-- Creazione della tabella Esercizio
CREATE TABLE IF NOT EXISTS Esercizio (
    id_esercizio INT PRIMARY KEY,
    nome_esercizio VARCHAR(100) ,
    ID_scheda INT,
    n_serie varchar(50),
    n_ripetizioni varchar(50),
    tempo_fase_concentrica varchar(50),
    tempo_fase_eccentrica varchar(50),
    FOREIGN KEY (ID_scheda) REFERENCES Scheda(ID_scheda)
);


CREATE TABLE IF NOT EXISTS Prodotto (
    Path VARCHAR(50) PRIMARY KEY,
    Descrizione text,
    Prezzo float,
    nome VARCHAR(50),
    marca VARCHAR(50)
);

