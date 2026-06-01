import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime
import os

# Configuração da página estilo Dark/Premium da Nordik
str_app.set_page_config(page_title="Nørdik Barbershop - Caixa", layout="wide")

# Estilização Avançada (Atmosfera Peaky Blinders & Premium)
str_app.markdown("""
    <style>
        /* IMPORTAÇÃO DE FONTES CLÁSSICAS */
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=Poppins:wght@300;400;600&display=swap');

        /* Fundo geral do app (Tijolos Escuros & Whisky Atmosférico) */
        .main { 
            background-image: linear-gradient(rgba(10, 10, 10, 0.96), rgba(10, 10, 10, 0.99)), url('https://images.unsplash.com/photo-1594911762742-124b823e5971?q=80&w=2000&auto=format&fit=crop');
            background-size: cover;
            background-attachment: fixed;
            color: #E0E0E0; 
            font-family: 'Poppins', sans-serif; 
        }
        
        /* Menu Lateral (Transparente e Refinado) */
        .css-1d391kg, .css-1aumxhk {
            background-color: rgba(20, 20, 20, 0.9) !important;
            border-right: 1px solid #1F1F1F;
        }

        /* Títulos e Subtítulos (Tipografia Serifada Clássica) */
        h1 { color: #D4AF37 !important; font-family: 'Cinzel', serif !important; font-weight: 700 !important; letter-spacing: 4px; text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin-bottom: 5px; }
        h2, h3 { color: #C0C0C0 !important; font-family: 'Poppins', sans-serif !important; font-weight: 300 !important; text-transform: uppercase; letter-spacing: 2px; }
        
        /* Cabeçalho Temático Customizado */
        .nordik-header {
            text-align: center;
            margin-bottom: 25px;
            padding: 20px;
            border-bottom: 2px solid #2C2C2C;
        }
        .nordik-header h1 { font-size: 32px; }
        .nordik-header p { color: #888888; text-transform: uppercase; font-size: 11px; letter-spacing: 2px; }

        /* Customização dos botões (Bronze Fosco) */
        .stButton>button { 
            background-color: #A08050; /* Cobre/Bronze Fosco */
            color: #0D0D0D; 
            font-weight: bold; 
            font-family: 'Poppins', sans-serif;
            border-radius: 4px; 
            border: 1px solid #705835;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover { background-color: #D4AF37; color: #0D0D0D; box-shadow: 0px 0px 15px rgba(212, 175, 55, 0.6); }
        
        /* Estilização dos Cards de Métricas (Bronze Refinado) */
        .nordik-card {
            background-color: rgba(30, 30, 30, 0.85); /* Semitransparente */
            border: 2px solid #D4AF37;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 15px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.6);
            backdrop-filter: blur(5px);
        }
        .nordik-card-title { color: #888888; font-family: 'Cinzel', serif; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 7px; }
        .nordik-card-value { color: #FFFFFF; font-size: 22px; font-weight: bold; font-family: 'Poppins', sans-serif; }
        
        /* Estilização das linhas do histórico */
        .nordik-row {
            background-color: rgba(20, 20, 20, 0.8);
            border: 1px solid #1F1F1F;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
""", unsafe_allow_html=True)

# Conexão com o banco de dados
def conectar_db():
    # Cria uma cópia do banco de dados para evitar problemas de thread
    conn = sqlite3.connect("nordik_web_cashflow_premium.db", check_same_thread=False)
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
# INTERFACE DO APP (Refinada Peaky Blinders)
# -----------------------------------------------------------------

# Cabeçalho Temático Customizado
str_app.markdown("""
    <div class="nordik-header">
        <h1>N Ø R D I K</h1>
        <p>CAIXA & DISTRIBUIÇÃO • ESTILO FORJADO NA LENDA</p>
    </div>
""", unsafe_allow_html=True)

# Menu Lateral para Cadastro
str_app.sidebar.header("➕ GERENCIAR LANÇAMENTO")

if "id_edicao" not in str_app.session_state:
    str_app.session_state.id_edicao = None

desc_padrao = ""
tipo_padrao = "Cortes e Serviços (Padrão)"
valor_padrao = 0.0

if str_app.session_state.id_edicao is not None:
    c = conn.cursor()
    c.execute("SELECT descricao, tipo, valor_bruto FROM fluxo_caixa WHERE id = ?", (str_app.session_state.id_edicao,))
    res = c.fetchone()
    if res:
        desc_padrao, tipo_padrao, valor_padrao = res
        str_app.sidebar.warning(f"EDITANDO ID: {str_app.session_state.id_edicao}")

desc = str_app.sidebar.text_input("Descrição do Item/Serviço:", value=desc_padrao, placeholder="Ex: Corte de Cabelo Cliente X")
tipo = str_app.sidebar.selectbox("Regra de Distribuição:", ["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"], index=["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"].index(tipo_padrao))
valor_bruto = str_app.sidebar.number_input("Valor Bruto (R$):", min_value=0.0, value=valor_padrao, step=5.0)

if str_app.sidebar.button("💾 SALVAR NO CAIXA"):
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
        else:
            # Atualizar Existente
            cursor.execute("""
                UPDATE fluxo_caixa 
                SET descricao=?, tipo=?, valor_bruto=?, socio_operacional=?, nordik=?, socio_investidor=?, barbeiro=?
                WHERE id=?
            """, (desc, tipo, valor_bruto, s_oper, nordik, s_inv, barb, str_app.session_state.id_edicao))
            str_app.session_state.id_edicao = None
            
        conn.commit()
        str_app.rerun()

if str_app.session_state.id_edicao is not None:
    if str_app.sidebar.button("❌ CANCELAR EDIÇÃO"):
        str_app.session_state.id_edicao = None
        str_app.rerun()

# -----------------------------------------------------------------
# EXIBIÇÃO DO DASHBOARD CENTRAL (CARDS CUSTOMIZADOS & RESPONSIVOS)
# -----------------------------------------------------------------
df = pd.read_sql_query("SELECT * FROM fluxo_caixa ORDER BY id DESC", conn)

if not df.empty:
    # Renderizando os Cards usando HTML/CSS Customizado para Mobile
    val_bruto = df['valor_bruto'].sum()
    val_oper = df['socio_operacional'].sum()
    val_nordik = df['nordik'].sum()
    val_inv = df['socio_investidor'].sum()
    val_barb = df['barbeiro'].sum()

    # Layout de cards empilhados elegantemente no celular (Um grande, quatro pequenos)
    str_app.markdown(f"""
        <div class="nordik-card" style="border: 2px solid #D4AF37; box-shadow: 0 15px 25px rgba(0,0,0,0.8);">
            <div class="nordik-card-title">FATURAMENTO BRUTO TOTAL</div>
            <div class="nordik-card-value" style="color: #D4AF37; font-size: 28px;">R$ {val_bruto:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Grid para as distribuições individuais
    col1, col2 = str_app.columns(2)
    with col1:
        str_app.markdown(f'<div class="nordik-card"><div class="nordik-card-title">Sócio Operacional</div><div class="nordik-card-value">R$ {val_oper:,.2f}</div></div>', unsafe_allow_html=True)
        str_app.markdown(f'<div class="nordik-card"><div class="nordik-card-title">Nordik (Marca)</div><div class="nordik-card-value">R$ {val_nordik:,.2f}</div></div>', unsafe_allow_html=True)
    with col2:
        str_app.markdown(f'<div class="nordik-card"><div class="nordik-card-title">Sócio Investidor</div><div class="nordik-card-value">R$ {val_inv:,.2f}</div></div>', unsafe_allow_html=True)
        str_app.markdown(f'<div class="nordik-card"><div class="nordik-card-title">Repasse Barbeiros</div><div class="nordik-card-value">R$ {val_barb:,.2f}</div></div>', unsafe_allow_html=True)
    
    str_app.write("---")
    
    # Lista Interativa de Movimentações (Design "Extrato Premium")
    str_app.subheader("📊 Histórico de Caixa")
    
    for index, row in df.iterrows():
        # Layout em container limpo para cada registro
        with str_app.container():
            c_info, c_acoes = str_app.columns([5, 1])
            
            with c_info:
                # Estilização interna da linha para parecer extrato bancário premium
                str_app.markdown(f"""
                    <div style="line-
