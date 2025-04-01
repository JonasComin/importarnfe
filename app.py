
from flask import Flask, render_template, request, redirect, send_file
import os
import sqlite3

app = Flask(__name__)

# Certifique-se de que a pasta uploads existe
os.makedirs("uploads", exist_ok=True)

def criar_banco():
    conn = sqlite3.connect("nfe.db")
    cur = conn.cursor()

    # Tabela de Notas
    cur.execute("""CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_nf TEXT,
        serie TEXT,
        emitente TEXT,
        destinatario TEXT,
        valor_total REAL,
        data_emissao TEXT
    )""")

    # Tabela de Itens
    cur.execute("""CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nota_id INTEGER,
        descricao TEXT,
        quantidade REAL,
        valor_unitario REAL,
        valor_total REAL,
        ncm TEXT,
        cst TEXT,
        FOREIGN KEY (nota_id) REFERENCES notas(id)
    )""")

    # Tabela de NCM
    cur.execute("""CREATE TABLE IF NOT EXISTS ncm_cadastro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ncm TEXT UNIQUE,
        substituicao_tributaria TEXT,
        data_atualizacao TEXT
    )""")

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/importar_xml")
def importar_xml():
    return render_template("importar.html")

@app.route("/ver_ncm")
def ver_ncm():
    return render_template("ncm.html")

@app.route("/notas")
def ver_notas():
    return render_template("notas.html")

@app.route("/itens")
def ver_itens():
    return render_template("itens.html")

@app.route("/editar_ncm/<int:id>")
def editar_ncm(id):
    return render_template("editar_ncm.html", id=id)

if __name__ == "__main__":
    criar_banco()
    app.run(host="0.0.0.0", port=10000)
