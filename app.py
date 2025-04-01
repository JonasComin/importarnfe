
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
import os
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta'
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB = 'banco.db'

def criar_banco()

def criar_tabelas_notas():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_nf TEXT,
            serie TEXT,
            emitente TEXT,
            destinatario TEXT,
            valor_total REAL,
            data_emissao TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER,
            descricao TEXT,
            quantidade REAL,
            valor_unitario REAL,
            valor_total REAL,
            FOREIGN KEY(nota_id) REFERENCES notas(id)
        )
    """)
    conn.commit()
    conn.close()

criar_tabelas_notas()
:
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ncm_cadastro (
            ncm TEXT PRIMARY KEY,
            substituicao_tributaria TEXT,
            data_atualizacao TEXT
        )
    """)
    conn.commit()
    try:
        cursor.execute("ALTER TABLE ncm_cadastro ADD COLUMN data_atualizacao TEXT")
    except:
        pass
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ncm')
def listar_ncm():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT ncm, substituicao_tributaria, data_atualizacao FROM ncm_cadastro ORDER BY ncm")
    dados = cursor.fetchall()
    conn.close()
    return render_template('ncm.html', ncms=dados)

@app.route('/importar', methods=['GET', 'POST'])
def importar_xml():
    if request.method == 'POST':
        arquivo = request.files['xmlfile']
        if arquivo.filename.endswith('.xml'):
            caminho = os.path.join(UPLOAD_FOLDER, secure_filename(arquivo.filename))
            arquivo.save(caminho)
            processar_xml(caminho)
            flash('XML importado com sucesso!', 'success')
        else:
            flash('Arquivo inválido. Envie um XML.', 'danger')
        return redirect(url_for('importar_xml'))
    return render_template('importar.html')

def processar_xml(caminho_xml):
    tree = ET.parse(caminho_xml)
    root = tree.getroot()
    ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
    
    ide = root.find('.//nfe:ide', ns)
    data_emissao = ide.find('nfe:dhEmi', ns)
    if data_emissao is not None:
        data_emissao = data_emissao.text[:10]
    else:
        data_emissao = datetime.now().strftime('%Y-%m-%d')

    
    # >>> INSERE NOTA
    emit = root.find('.//nfe:emit', ns)
    dest = root.find('.//nfe:dest', ns)
    infNFe = root.find('.//nfe:infNFe', ns)
    numero_nf = ide.find('nfe:nNF', ns).text if ide is not None else ''
    serie = ide.find('nfe:serie', ns).text if ide is not None else ''
    emitente = emit.find('nfe:xNome', ns).text if emit is not None else ''
    destinatario = dest.find('nfe:xNome', ns).text if dest is not None else ''
    valor_total = root.find('.//nfe:vNF', ns).text if root.find('.//nfe:vNF', ns) is not None else 0.0

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO notas (numero_nf, serie, emitente, destinatario, valor_total, data_emissao) VALUES (?, ?, ?, ?, ?, ?)",
                   (numero_nf, serie, emitente, destinatario, valor_total, data_emissao))
    nota_id = cursor.lastrowid
    conn.commit()
    conn.close()

    for det in root.findall('.//nfe:det', ns):

        prod = det.find('nfe:prod', ns)
        imposto = det.find('nfe:imposto', ns)
        icms = imposto.find('nfe:ICMS', ns)[0]
        
        ncm = prod.find('nfe:NCM', ns).text if prod.find('nfe:NCM', ns) is not None else ''
        cst = icms.find('nfe:CST', ns).text if icms.find('nfe:CST', ns) is not None else ''

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ncm_cadastro WHERE ncm=?", (ncm,))
        existe = cursor.fetchone()
        if not existe:
            subst = 'Sim' if cst == '60' else 'Não'
            cursor.execute("INSERT INTO ncm_cadastro (ncm, substituicao_tributaria, data_atualizacao) VALUES (?, ?, ?)",
                           (ncm, subst, data_emissao))
            conn.commit()

        # Inserir item da nota
        descricao = prod.find('nfe:xProd', ns).text if prod.find('nfe:xProd', ns) is not None else ''
        qtd = float(prod.find('nfe:qCom', ns).text.replace(',', '.')) if prod.find('nfe:qCom', ns) is not None else 0
        vunit = float(prod.find('nfe:vUnCom', ns).text.replace(',', '.')) if prod.find('nfe:vUnCom', ns) is not None else 0
        vtotal = float(prod.find('nfe:vProd', ns).text.replace(',', '.')) if prod.find('nfe:vProd', ns) is not None else 0
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO itens (nota_id, descricao, quantidade, valor_unitario, valor_total) VALUES (?, ?, ?, ?, ?)",
                       (nota_id, descricao, qtd, vunit, vtotal))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    criar_banco()

def criar_tabelas_notas():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_nf TEXT,
            serie TEXT,
            emitente TEXT,
            destinatario TEXT,
            valor_total REAL,
            data_emissao TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota_id INTEGER,
            descricao TEXT,
            quantidade REAL,
            valor_unitario REAL,
            valor_total REAL,
            FOREIGN KEY(nota_id) REFERENCES notas(id)
        )
    """)
    conn.commit()
    conn.close()

criar_tabelas_notas()

    app.run(debug=True)

@app.route('/ncm/editar/<ncm>', methods=['GET', 'POST'])
def editar_ncm(ncm):
    if request.method == 'POST':
        nova_subst = request.form['subst']
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("UPDATE ncm_cadastro SET substituicao_tributaria = ? WHERE ncm = ?", (nova_subst, ncm))
        conn.commit()

        # Inserir item da nota
        descricao = prod.find('nfe:xProd', ns).text if prod.find('nfe:xProd', ns) is not None else ''
        qtd = float(prod.find('nfe:qCom', ns).text.replace(',', '.')) if prod.find('nfe:qCom', ns) is not None else 0
        vunit = float(prod.find('nfe:vUnCom', ns).text.replace(',', '.')) if prod.find('nfe:vUnCom', ns) is not None else 0
        vtotal = float(prod.find('nfe:vProd', ns).text.replace(',', '.')) if prod.find('nfe:vProd', ns) is not None else 0
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO itens (nota_id, descricao, quantidade, valor_unitario, valor_total) VALUES (?, ?, ?, ?, ?)",
                       (nota_id, descricao, qtd, vunit, vtotal))
        conn.commit()
        conn.close()

        flash("NCM atualizado com sucesso!", "success")
        return redirect(url_for('listar_ncm'))

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT substituicao_tributaria FROM ncm_cadastro WHERE ncm = ?", (ncm,))
    resultado = cursor.fetchone()
    conn.close()
    return render_template("editar_ncm.html", ncm=ncm, subst=resultado[0] if resultado else '')

@app.route('/ncm/excluir/<ncm>')
def excluir_ncm(ncm):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ncm_cadastro WHERE ncm = ?", (ncm,))
    conn.commit()
    conn.close()
    flash("NCM excluído com sucesso!", "success")
    return redirect(url_for('listar_ncm'))

@app.route('/ncm/exportar/excel')
def exportar_ncm_excel():
    conn = sqlite3.connect(DB)
    df = pd.read_sql_query("SELECT * FROM ncm_cadastro ORDER BY ncm", conn)
    conn.close()
    caminho = os.path.join("static", "ncm_exportado.xlsx")
    df.to_excel(caminho, index=False)
    return send_file(caminho, as_attachment=True)

@app.route('/ncm/exportar/pdf')
def exportar_ncm_pdf():
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ncm_cadastro ORDER BY ncm")
    dados = cursor.fetchall()
    conn.close()

    pdf_path = os.path.join("static", "relatorio_ncm.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    estilos = getSampleStyleSheet()
    elementos = [Paragraph("Relatório de NCMs", estilos["Title"]), Spacer(1, 12)]
    tabela = Table([["NCM", "Substituição Tributária", "Data de Atualização"]] + dados)
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.gray),
        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))
    elementos.append(tabela)
    doc.build(elementos)
    return send_file(pdf_path, as_attachment=True)

@app.route('/notas')
def listar_notas():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero_nf, serie, emitente, destinatario, valor_total, data_emissao FROM notas ORDER BY data_emissao DESC")
    notas = cursor.fetchall()
    conn.close()
    return render_template("notas.html", notas=notas)

@app.route('/notas/<int:nota_id>')
def ver_itens(nota_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT descricao, quantidade, valor_unitario, valor_total FROM itens WHERE nota_id = ?", (nota_id,))
    itens = cursor.fetchall()
    conn.close()
    return render_template("itens.html", itens=itens, nota_id=nota_id)
