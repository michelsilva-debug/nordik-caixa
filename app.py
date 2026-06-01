import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da página estilo Dark/Premium da Nordik
str_app.set_page_config(page_title="Nørdik Barbershop - Caixa", layout="wide")

# Estilização customizada (Cores Escuras e Destaques em Dourado)
str_app.markdown("""
    <style>
        .main { background-color: #1A1A1A; color: #FFFFFF; }
        h1, h2, h3 { color: #D4AF37 !important; }
        .stButton>button { background-color: #D4AF37; color: #1A1A1A; font-weight: bold; width: 100%; }
        .stButton>button:hover { background-color: #F5E6CC; color: #1A1A1A; }
    </style>
""", unsafe_allow_html=True)

# Conexão com o banco de dados
def conectar_db():
    conn = sqlite3.connect("nordik_web_cashflow.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fluxo_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            tipo TEXT,
            valor_bruto REAL,
            socio_operacional REAL,
            nordik REAL,
            socio_investidor REAL,
            barbeiro REAL
        )
    """)
    conn.commit()
    return conn

conn = conectar_db()

def calcular_divisao(tipo, valor_bruto):
    if tipo == "Cortes e Serviços (Padrão)":
        return valor_bruto * 0.60, valor_bruto * 0.25, valor_bruto * 0.15, 0.0
    elif tipo == "Bebidas e Produtos":
        return valor_bruto * 0.30, valor_bruto * 0.40, valor_bruto * 0.30, 0.0
    elif tipo == "Novos Barbeiros":
        return valor_bruto * 0.05, valor_bruto * 0.10, valor_bruto * 0.20, valor_bruto * 0.65
    return 0.0, 0.0, 0.0, 0.0

# -----------------------------------------------------------------
# INTERFACE DO APP
# -----------------------------------------------------------------
str_app.title("N Ø R D I K    B A R B E R S H O P")
str_app.subheader("Sistema de Fluxo de Caixa & Distribuição")

# Menu Lateral para Cadastro
str_app.sidebar.header("➕ Gerenciar Lançamentos")

# Sistema para controlar se estamos editando algo
if "id_edicao" not in str_app.session_state:
    str_app.session_state.id_edicao = None

desc_padrao = ""
tipo_padrao = "Cortes e Serviços (Padrão)"
valor_padrao = 0.0

# Se houver um ID sob edição, busca os dados antigos para preencher o formulário
if str_app.session_state.id_edicao is not None:
    c = conn.cursor()
    c.execute("SELECT descricao, tipo, valor_bruto FROM fluxo_caixa WHERE id = ?", (str_app.session_state.id_edicao,))
    res = c.fetchone()
    if res:
        desc_padrao, tipo_padrao, valor_padrao = res
        str_app.sidebar.warning(f"Editando Registro ID: {str_app.session_state.id_edicao}")

desc = str_app.sidebar.text_input("Descrição do Item/Serviço:", value=desc_padrao)
tipo = str_app.sidebar.selectbox("Regra de Distribuição:", ["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"], index=["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"].index(tipo_padrao))
valor_bruto = str_app.sidebar.number_input("Valor Bruto (R$):", min_value=0.0, value=valor_padrao, step=10.0)

if str_app.sidebar.button("💾 Salvar Registro"):
    if desc and valor_bruto > 0:
        s_oper, nordik, s_inv, barb = calcular_divisao(tipo, valor_bruto)
        cursor = conn.cursor()
        
        if str_app.session_state.id_edicao is None:
            # Inserir Novo
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor.execute("""
                INSERT INTO fluxo_caixa (data, descricao, tipo, valor_bruto, socio_operacional, nordik, socio_investidor, barbeiro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_atual, desc, tipo, valor_bruto, s_oper, nordik, s_inv, barb))
            str_app.sidebar.success("Lançamento Adicionado!")
        else:
            # Atualizar Existente
            cursor.execute("""
                UPDATE fluxo_caixa 
                SET descricao=?, tipo=?, valor_bruto=?, socio_operacional=?, nordik=?, socio_investidor=?, barbeiro=?
                WHERE id=?
            """, (desc, tipo, valor_bruto, s_oper, nordik, s_inv, barb, str_app.session_state.id_edicao))
            str_app.session_state.id_edicao = None
            str_app.sidebar.success("Lançamento Atualizado!")
            
        conn.commit()
    else:
        str_app.sidebar.error("Preencha a descrição e o valor corretamente.")

if str_app.session_state.id_edicao is not None:
    if str_app.sidebar.button("❌ Cancelar Edição"):
        str_app.session_state.id_edicao = None
        str_app.rerun()

# -----------------------------------------------------------------
# EXIBIÇÃO DO DASHBOARD CENTRAL
# -----------------------------------------------------------------
df = pd.read_sql_query("SELECT * FROM fluxo_caixa ORDER BY id DESC", conn)

if not df.empty:
    # Cards de Resumo de Caixa
    c1, c2, c3, c4, c5 = str_app.columns(5)
    c1.metric("Faturamento Bruto", f"R$ {df['valor_bruto'].sum():,.2f}")
    c2.metric("Sócio Operacional", f"R$ {df['socio_operacional'].sum():,.2f}")
    c3.metric("Nordik (Marca)", f"R$ {df['nordik'].sum():,.2f}")
    c4.metric("Sócio Investidor", f"R$ {df['socio_investidor'].sum():,.2f}")
    c5.metric("Barbeiros", f"R$ {df['barbeiro'].sum():,.2f}")
    
    str_app.write("---")
    
    # Lista Interativa de Movimentações
    str_app.subheader("📊 Histórico de Transações")
    
    # Criando colunas dinâmicas para simular botões de Editar/Deletar na tabela
    for index, row in df.iterrows():
        col_id, col_data, col_desc, col_tipo, col_val, col_edit, col_del = str_app.columns([1, 2, 3, 3, 2, 1, 1])
        
        col_id.write(f"**#{row['id']}**")
        col_data.write(row['data'])
        col_desc.write(row['descricao'])
        col_tipo.write(row['tipo'])
        col_val.write(f"R$ {row['valor_bruto']:.2f}")
        
        # Botão Editar
        if col_edit.button("✏️", key=f"edit_{row['id']}"):
            str_app.session_state.id_edicao = int(row['id'])
            str_app.rerun()
            
        # Botão Excluir
        if col_del.button("🗑️", key=f"del_{row['id']}"):
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fluxo_caixa WHERE id=?", (row['id'],))
            conn.commit()
            str_app.success(f"Registro #{row['id']} removido.")
            str_app.rerun()
else:
    str_app.info("Nenhum lançamento registrado no fluxo de caixa ainda.")
