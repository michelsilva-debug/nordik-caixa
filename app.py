import streamlit as str_app
import sqlite3
import pandas as pd
from datetime import datetime

# Configuração da página estilo Dark/Premium da Nordik
str_app.set_page_config(page_title="Nørdik Barbershop - Caixa", layout="wide")

# Estilização Avançada (Fundo comercial escuro, texto limpo e detalhes em ouro fosco)
str_app.markdown("""
    <style>
        /* Fundo geral do app */
        .main { background-color: #0D0D0D; color: #E5E5E5; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
        
        /* Títulos e Subtítulos */
        h1, h2, h3 { color: #D4AF37 !important; font-weight: 300 !important; letter-spacing: 2px; text-transform: uppercase; }
        
        /* Customização dos botões do menu lateral */
        .stButton>button { 
            background-color: #D4AF37; 
            color: #0D0D0D; 
            font-weight: bold; 
            border-radius: 6px; 
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover { background-color: #FFF; color: #0D0D0D; box-shadow: 0px 0px 10px rgba(212, 175, 55, 0.5); }
        
        /* Estilização dos Cards de Faturamento (Métricas) */
        .nordik-card {
            background-color: #1A1A1A;
            border: 1px solid #2C2C2C;
            border-left: 4px solid #D4AF37;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .nordik-card-title { color: #888888; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px; }
        .nordik-card-value { color: #FFFFFF; font-size: 20px; font-weight: bold; }
        
        /* Estilização das linhas do histórico */
        .nordik-row {
            background-color: #141414;
            border: 1px solid #1F1F1F;
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
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
str_app.title("N Ø R D I K")
str_app.caption("FLUXO DE CAIXA & DISTRIBUIÇÃO PREMIUM")

# Menu Lateral para Cadastro
str_app.sidebar.header("➕ NOVO LANÇAMENTO")

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
        str_app.sidebar.warning(f"Editando ID: {str_app.session_state.id_edicao}")

desc = str_app.sidebar.text_input("Descrição:", value=desc_padrao, placeholder="Ex: Corte do Cliente X")
tipo = str_app.sidebar.selectbox("Regra de Divisão:", ["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"], index=["Cortes e Serviços (Padrão)", "Bebidas e Produtos", "Novos Barbeiros"].index(tipo_padrao))
valor_bruto = str_app.sidebar.number_input("Valor Bruto (R$):", min_value=0.0, value=valor_padrao, step=5.0)

if str_app.sidebar.button("💾 SALVAR NO CAIXA"):
    if desc and valor_bruto > 0:
        s_oper, nordik, s_inv, barb = calcular_divisao(tipo, valor_bruto)
        cursor = conn.cursor()
        
        if str_app.session_state.id_edicao is None:
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor.execute("""
                INSERT INTO fluxo_caixa (data, descricao, tipo, valor_bruto, socio_operacional, nordik, socio_investidor, barbeiro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (data_atual, desc, tipo, valor_bruto, s_oper, nordik, s_inv, barb))
        else:
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
# EXIBIÇÃO DO DASHBOARD CENTRAL (CARDS CUSTOMIZADOS)
# -----------------------------------------------------------------
df = pd.read_sql_query("SELECT * FROM fluxo_caixa ORDER BY id DESC", conn)

if not df.empty:
    # Renderizando os Cards usando HTML/CSS Customizado para Mobile
    val_bruto = df['valor_bruto'].sum()
    val_oper = df['socio_operacional'].sum()
    val_nordik = df['nordik'].sum()
    val_inv = df['socio_investidor'].sum()
    val_barb = df['barbeiro'].sum()

    # Layout de cards empilhados elegantemente no celular
    str_app.markdown(f"""
        <div class="nordik-card" style="border-left-color: #D4AF37;">
            <div class="nordik-card-title">Faturamento Bruto Acumulado</div>
            <div class="nordik-card-value" style="color: #D4AF37;">R$ {val_bruto:,.2f}</div>
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
    
    # Lista Interativa de Movimentações
    str_app.subheader("📊 Histórico de Caixa")
    
    for index, row in df.iterrows():
        # Layout em container limpo para cada registro
        with str_app.container():
            c_info, c_acoes = str_app.columns([5, 1])
            
            with c_info:
                str_app.markdown(f"""
                    <div style="line-height: 1.4; margin-bottom: 5px;">
                        <span style="color: #D4AF37; font-weight: bold;">#{row['id']} - {row['descricao']}</span><br>
                        <small style="color: #666;">{row['data']} | {row['tipo']}</small><br>
                        <span style="font-size: 16px; font-weight: bold; color: #FFF;">R$ {row['valor_bruto']:.2f}</span>
                    </div>
                """, unsafe_allow_html=True)
            
            with c_acoes:
                # Botões compactos alinhados lado a lado
                sub_c1, sub_c2 = str_app.columns(2)
                if sub_c1.button("✏️", key=f"edit_{row['id']}"):
                    str_app.session_state.id_edicao = int(row['id'])
                    str_app.rerun()
                if sub_c2.button("🗑️", key=f"del_{row['id']}"):
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM fluxo_caixa WHERE id=?", (row['id'],))
                    conn.commit()
                    str_app.rerun()
            str_app.markdown('<hr style="border-color: #1F1F1F; margin: 5px 0 15px 0;">', unsafe_allow_html=True)
else:
    str_app.info("Nenhum lançamento registrado no fluxo de caixa ainda.")
