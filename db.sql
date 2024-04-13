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

-- Creazione della tabella Scheda
CREATE TABLE IF NOT EXISTS Scheda (
    ID_scheda INT PRIMARY KEY,
    ID_account INT,
    FOREIGN KEY (ID_account) REFERENCES Account(ID_account)
);

-- Creazione della tabella Esercizio
CREATE TABLE IF NOT EXISTS Esercizio (
    nome_esercizio VARCHAR(100) PRIMARY KEY,
    ID_scheda INT,
    FOREIGN KEY (ID_scheda) REFERENCES Scheda(ID_scheda)
);

-- Creazione della tabella Serie
CREATE TABLE IF NOT EXISTS Serie (
    ID_serie INT PRIMARY KEY,
    n_serie INT,
    nome_esercizio VARCHAR(100),
    FOREIGN KEY (nome_esercizio) REFERENCES Esercizio(nome_esercizio)
);

-- Creazione della tabella Ripetizioni_serie
CREATE TABLE IF NOT EXISTS Ripetizioni_serie (
    id_ripetizione INT PRIMARY KEY,
    n_ripetizioni INT,
    tempo_fase_concentrica INT,
    tempo_fase_eccentrica INT,
    ID_serie INT,
    FOREIGN KEY (ID_serie) REFERENCES Serie(ID_serie)
);
