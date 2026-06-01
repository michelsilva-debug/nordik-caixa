import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da página estilo Dark/Premium da Nordik
str_app.set_page_config(page_title="Nørdik Barbershop - Caixa", layout="wide")

# Interface Avançada: Atmosfera Peaky Blinders & Industrial Chic
str_app.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Montserrat:wght@300;400;600&display=swap');

        /* Fundo temático com textura de tijolo escuro londrino */
        .main { 
            background-image: linear-gradient(rgba(10, 10, 10, 0.93), rgba(15, 15, 15, 0.97)), url('https://images.unsplash.com/photo-1541963463532-d68292c34b19?q=80&w=1000&auto=format&fit=crop');
            background-size: cover;
            background-attachment: fixed;
            color: #E2E2E2; 
            font-family: 'Montserrat', sans-serif; 
        }

        /* Títulos principais no estilo pub/alfaiataria clássica */
        h1 { 
            color: #D4AF37 !important; 
            font-family: 'Cinzel', serif !important; 
            font-weight: 700 !important; 
            letter-spacing: 3px; 
            text-transform: uppercase; 
            text-shadow: 2px 2px 8px rgba(0,0,0,0.9);
            text-align: center;
            margin-bottom: 0px;
        }
        
        .sub-nordik {
            text-align: center;
            color: #8A8A8A;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 25px;
            font-weight: 600;
        }

        /* Cards de faturamento inspirados em metal/couro envelhecido */
        .card-peaky {
            background: linear-gradient(135deg, #1C1C1C 0%, #121212 100%);
            border: 1px solid #332A15;
            border-top: 3px solid #D4AF37;
            padding: 18px;
            border-radius: 4px;
            margin-bottom: 12px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.6);
        }
        .card-peaky-title { 
            color: #8C8C8C; 
            font-family: 'Cinzel', serif; 
            font-size: 10px; 
            letter-spacing: 1px; 
            text-transform: uppercase; 
            margin-bottom: 4px; 
        }
        .card-peaky-value { 
            color: #FFFFFF; 
            font-size: 22px; 
            font-weight: bold; 
        }

        /* Botões do Menu Lateral em Ouro Velho */
        .stButton>button { 
            background: linear-gradient(135deg, #A38049 0%, #7A5E33 100%) !important;
            color: #000000 !important; 
            font-weight: 700 !important; 
            border-radius: 3px !important; 
            border: 1px solid #5C4624 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 100%;
        }
        .stButton>button:hover { 
            background: #D4AF37 !important;
            box-shadow: 0px 0px 12px rgba(212, 175, 55, 0.5); 
        }

        /* Lista de histórico limpa */
        .item-historico {
            background-color: rgba(20, 20, 20, 0.75);
            border-left: 2px solid #A38049;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 2px;
        }
    </style>
""", unsafe_allow_html=True)

# Inicialização do Banco de Dados
def iniciar_banco():
    conn = sqlite3.connect("nordik_caixa_v2.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fluxo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            descricao TEXT,
            tipo TEXT,
            valor REAL,
            operacional REAL,
            nordik REAL,
            investidor REAL,
            barbeiro REAL
        )
    """)
    conn.commit()
    return conn

conn = iniciar_banco()

# Regras de negócio da divisão
def dividir_valores(tipo, valor_total):
    if tipo == "Cortes e Serviços (Padrão)":
        return valor_total * 0.60, valor_total * 0.25, valor_total * 0.15, 0.0
    elif tipo == "Bebidas e Produtos":
        return valor_total * 0.30, valor_total * 0.40, valor_total * 0.30, 0.0
    elif tipo == "Novos Barbeiros":
        return valor_total * 0.05, valor_total * 0.10, valor_total * 0.20, valor_total * 0.65
    return 0.0, 0.0, 0.0, 0.0

# Cabeçalho da Marca
str_app.markdown("<h1>N Ø R D I K</h1>", unsafe_allow_html=True)
str_app.markdown("<p class='sub-nordik'>CONTA DE CAIXA • POR ORDEM DOS PEAKY BLINDERS</p>", unsafe_allow_html=True)

# Gerenciamento de Estado de Edição
if "edit_id" not in str_app.session_state:
    str_app.session_state.edit_id = None

# Sidebar elegante
str_app.sidebar.header("🥃 NOVO REGISTRO")

# Valores padrão caso seja edição
def_desc, def_tipo, def_valor = "", "Cortes e Serviços (Padrão)", 0.0
if str_app.session_state.edit_id is not None:
    c = conn.cursor()
    c.execute("SELECT descricao, tipo, valor FROM fluxo WHERE id = ?", (str_app.session_state.edit_id,))
    item = c.fetchone()
    if item:
        def_desc, def_tipo, def_valor = item
        str_app.sidebar.warning(f"Modificando ID #{str_app.session_state.edit_id}")

campo_desc = str_app.sidebar.text_input("Descrição:", value=def_desc)
campo_tipo = str_app.sidebar.selectbox("Regra de Divisão:", ["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"], index=["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"].index(def_tipo))
campo_valor = str_app.sidebar.number_input("Valor Bruto (R$):", min_value=0.0, value=def_valor, step=10.0)

if str_app.sidebar.button("REGISTRAR MOVIMENTAÇÃO"):
    if campo_desc and campo_valor > 0:
        op, nk, inv, barb = dividir_valores(campo_tipo, campo_valor)
        cursor = conn.cursor()
        
        if str_app.session_state.edit_id is None:
            data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor.execute("""
                INSERT INTO fluxo (data, descricao, tipo, valor, operacional, nordik, investidor, barbeiro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_str, campo_desc, campo_tipo, campo_valor, op, nk, inv, barb))
        else:
            cursor.execute("""
                UPDATE fluxo SET descricao=?, tipo=?, valor=?, operacional=?, nordik=?, investidor=?, barbeiro=? WHERE id=?
            """, (campo_desc, campo_tipo, campo_valor, op, nk, inv, str_app.session_state.edit_id))
            str_app.session_state.edit_id = None
            
        conn.commit()
        str_app.rerun()

if str_app.session_state.edit_id is not None:
    if str_app.sidebar.button("CANCELAR ALTERAÇÃO"):
        str_app.session_state.edit_id = None
        str_app.rerun()

# Leitura e construção do Dashboard central
df = pd.read_sql_query("SELECT * FROM fluxo ORDER BY id DESC", conn)

if not df.empty:
    total_b = df['valor'].sum()
    total_op = df['operacional'].sum()
    total_nk = df['nordik'].sum()
    total_inv = df['investidor'].sum()
    total_barb = df['barbeiro'].sum()

    # Painel Principal em HTML limpo sem f-strings quebradas
    str_app.markdown(f"""
        <div class="card-peaky" style="border-top-color: #D4AF37;">
            <div class="card-peaky-title">Faturamento Bruto Geral</div>
            <div class="card-peaky-value" style="color: #D4AF37; font-size: 28px;">R$ {total_b:,.2f}</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2 = str_app.columns(2)
    with c1:
        str_app.markdown(f'<div class="card-peaky"><div class="card-peaky-title">Sócio Operacional (60%/30%/5%)</div><div class="card-peaky-value">R$ {total_op:,.2f}</div></div>', unsafe_allow_html=True)
        str_app.markdown(f'<div class="card-peaky"><div class="card-peaky-title">Nørdik (Marca) (25%/40%/10%)</div><div class="card-peaky-value">R$ {total_nk:,.2f}</div></div>', unsafe_allow_html=True)
    with c2:
        str_app.markdown(f'<div class="card-peaky"><div class="card-peaky-title">Sócio Investidor (15%/30%/20%)</div><div class="card-peaky-value">R$ {total_inv:,.2f}</div></div>', unsafe_allow_html=True)
        str_app.markdown(f'<div class="card-peaky"><div class="card-peaky-title">Repasse Barbeiros (0%/0%/65%)</div><div class="card-peaky-value">R$ {total_barb:,.2f}</div></div>', unsafe_allow_html=True)

    str_app.markdown("<h3 style='margin-top:20px; font-family:Cinzel, serif; color:#D4AF37;'>📜 LIVRO DE ENTRADAS</h3>", unsafe_allow_html=True)

    for idx, row in df.iterrows():
        with str_app.container():
            col_info, col_btn = str_app.columns([4, 1.2])
            with col_info:
                str_app.markdown(f"""
                    <div class="item-historico">
                        <strong style="color:#D4AF37; font-family:'Cinzel', serif;">#{row['id']} - {row['descricao']}</strong><br>
                        <span style="font-size:11px; color:#777;">{row['data']} | {row['tipo']}</span><br>
                        <span style="font-size:16px; font-weight:bold; color:#FFF;">R$ {row['valor']:.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_btn:
                str_app.markdown("<div style='padding-top:10px;'></div>", unsafe_allow_html=True)
                sub_c1, sub_c2 = str_app.columns(2)
                if sub_c1.button("✏️", key=f"e_{row['id']}"):
                    str_app.session_state.edit_id = int(row['id'])
                    str_app.rerun()
                if sub_c2.button("🗑️", key=f"d_{row['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM fluxo WHERE id=?", (row['id'],))
                    conn.commit()
                    str_app.rerun()
else:
    str_app.info("Nenhum registro encontrado no livro de caixa.")
