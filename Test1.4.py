import streamlit as st
import pandas as pd
import numpy as np
import json
from io import StringIO
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configurações iniciais
st.set_page_config(page_title="Football Studio Pro – Análise Estratégica", layout="wide", initial_sidebar_state="expanded")

# Disclaimer ético
st.sidebar.markdown("""
### ⚠️ Aviso Importante
Esta ferramenta é para fins analíticos e educacionais. Jogos de azar envolvem riscos financeiros. Não garante vitórias; resultados passados não predizem futuros. Aposte responsavelmente.
""")

# Inicialização do estado da sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

# Função para adicionar resultado com validação
def adicionar_resultado(valor):
    if valor in ["C", "V", "E", "🔽"]:
        st.session_state.historico.append(valor)
    else:
        st.error("Valor inválido. Use apenas C, V, E ou 🔽.")

# Funções analíticas (usando os últimos N válidos, configurável)
@st.cache_data
def get_valores(h, n=27):
    return [r for r in h if r in ["C", "V", "E"]][-n:]

def maior_sequencia(h, n=27):
    h = get_valores(h, n)
    if not h:
        return 0
    max_seq = atual = 1
    for i in range(1, len(h)):
        if h[i] == h[i - 1]:
            atual += 1
            max_seq = max(max_seq, atual)
        else:
            atual = 1
    return max_seq

def sequencia_final(h, n=27):
    h = get_valores(h, n)
    if not h:
        return 0
    atual = h[-1]
    count = 1
    for i in range(len(h) - 2, -1, -1):
        if h[i] == atual:
            count += 1
        else:
            break
    return count

def alternancia(h, n=27):
    h = get_valores(h, n)
    return sum(1 for i in range(1, len(h)) if h[i] != h[i - 1])

def eco_visual(h, n=27):
    h = get_valores(h, n)
    if len(h) < 12:
        return "Poucos dados"
    return "Detectado" if h[-6:] == h[-12:-6] else "Não houve"

def eco_parcial(h, n=27):
    h = get_valores(h, n)
    if len(h) < 12:
        return "Poucos dados"
    anterior = h[-12:-6]
    atual = h[-6:]
    semelhantes = sum(1 for a, b in zip(anterior, atual) if a == b or (a in ['C', 'V'] and b in ['C', 'V']))
    return f"{semelhantes}/6 semelhantes"

def dist_empates(h, n=27):
    h = get_valores(h, n)
    empates = [i for i, r in enumerate(h) if r == 'E']
    if len(empates) < 2:
        return "N/A"
    return empates[-1] - empates[-2]

def blocos_espelhados(h, n=27):
    h = get_valores(h, n)
    cont = 0
    for i in range(len(h) - 5):
        if h[i:i + 3] == h[i + 3:i + 6][::-1]:
            cont += 1
    return cont

def alternancia_por_linha(h, linha_size=9, n=27):
    h = get_valores(h, n)
    linhas = [h[i:i + linha_size] for i in range(0, len(h), linha_size)]
    return [sum(1 for j in range(1, len(linha)) if linha[j] != linha[j - 1]) for linha in linhas]

def tendencia_final(h, window=5, n=27):
    h = get_valores(h, n)
    ult = h[-window:]
    return f"{ult.count('C')}C / {ult.count('V')}V / {ult.count('E')}E"

# Análises avançadas com estatísticas
@st.cache_data
def prob_condicional(h, n=27):
    h = get_valores(h, n)
    if len(h) < 2:
        return {"Após C": {}, "Após V": {}, "Após E": {}}
    df = pd.DataFrame({"Atual": h[:-1], "Próximo": h[1:]})
    trans = pd.crosstab(df['Atual'], df['Próximo'], normalize='index') * 100
    return trans.to_dict(orient='index')

@st.cache_data
def teste_aleatoriedade(h, n=27):
    h = get_valores(h, n)
    if len(h) < 10:
        return "Poucos dados para teste"
    # Teste de runs (Wald-Wolfowitz) para aleatoriedade
    runs = alternancia(h, n) + 1
    n1 = h.count('C') + h.count('V')  # Considerando C/V como uma classe vs E
    n2 = h.count('E')
    if n1 == 0 or n2 == 0:
        return "Dados insuficientes"
    mu = (2 * n1 * n2) / (n1 + n2) + 1
    sigma = np.sqrt((2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / ((n1 + n2)**2 * (n1 + n2 - 1)))
    z = (runs - mu) / sigma
    p_value = stats.norm.sf(abs(z)) * 2
    return f"Z-score: {z:.2f}, p-value: {p_value:.4f} ({'Aleatório' if p_value > 0.05 else 'Não aleatório'})"

# Função de cor para bolhas
def bolha_cor(r):
    return {
        "C": "🟥",
        "V": "🟦",
        "E": "🟨",
        "🔽": "⬇️"
    }.get(r, "⬜")

# Sugestão preditiva melhorada com probabilidades
def sugestao(h, n=27):
    valores = get_valores(h, n)
    if not valores:
        return "Insira resultados para gerar previsão."
    ult = valores[-1]
    seq = sequencia_final(h, n)
    eco = eco_visual(h, n)
    parcial = eco_parcial(h, n)
    contagens = {
        "C": valores.count("C"),
        "V": valores.count("V"),
        "E": valores.count("E")
    }
    probs = prob_condicional(h, n).get(ult, {"C": 33, "V": 33, "E": 34})

    if seq >= 5 and ult in ["C", "V"]:
        cor_inversa = "V" if ult == "C" else "C"
        return f"🔁 Sequência de {seq} {bolha_cor(ult)} — possível reversão para {bolha_cor(cor_inversa)} (Prob: {probs.get(cor_inversa, 0):.0f}%)"
    if ult == "E":
        return f"🟨 Empate recente — possível 🟥 ({probs.get('C', 0):.0f}%) ou 🟦 ({probs.get('V', 0):.0f}%)"
    if eco == "Detectado" or parcial.startswith(("5", "6")):
        return f"🔄 Eco detectado — repetir {bolha_cor(ult)} (Prob: {probs.get(ult, 0):.0f}%)"
    maior = max(contagens, key=contagens.get)
    return f"📊 Tendência para {bolha_cor(maior)} ({maior}) (Prob: {probs.get(maior, 0):.0f}%)"

# Interface Principal
st.title("🎲 Football Studio Pro — Leitura Estratégica Avançada")

# Sidebar para configurações
with st.sidebar:
    st.header("Configurações")
    n_analise = st.slider("Jogadas para análise", min_value=10, max_value=100, value=27, step=1)
    linha_size = st.slider("Tamanho da linha visual", min_value=6, max_value=12, value=9, step=1)
    tendencia_window = st.slider("Janela de tendência final", min_value=3, max_value=10, value=5, step=1)
    
    st.header("Gerenciamento de Histórico")
    if st.button("🧹 Limpar histórico"):
        st.session_state.historico = []
        st.rerun()
    
    # Exportar histórico
    hist_json = json.dumps(st.session_state.historico)
    st.download_button("📥 Baixar histórico (JSON)", data=hist_json, file_name="historico.json")
    
    # Importar histórico
    uploaded_file = st.file_uploader("📤 Carregar histórico (JSON ou CSV)", type=["json", "csv"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".json"):
                data = json.load(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
                data = df.iloc[:, 0].tolist()  # Assume primeira coluna
            st.session_state.historico.extend([str(v).upper() for v in data if str(v).upper() in ["C", "V", "E", "🔽"]])
            st.success("Histórico carregado com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao carregar: {e}")

# Entrada manual
st.subheader("Entrada de Resultados")
col1, col2, col3, col4 = st.columns(4)
if col1.button("➕ Casa (C)", key="btn_c"): adicionar_resultado("C")
if col2.button("➕ Visitante (V)", key="btn_v"): adicionar_resultado("V")
if col3.button("➕ Empate (E)", key="btn_e"): adicionar_resultado("E")
if col4.button("🗂️ Novo baralho (🔽)", key="btn_deck"): adicionar_resultado("🔽")

# Undo última entrada
if st.button("↩️ Desfazer última entrada") and st.session_state.historico:
    st.session_state.historico.pop()
    st.rerun()

h = st.session_state.historico

# Sugestão preditiva
st.subheader("🎯 Sugestão de Entrada")
st.success(sugestao(h, n=n_analise))

# Histórico visual interativo
st.subheader(f"🧾 Histórico Visual (Zona ativa: últimos {n_analise})")
h_reverso = h[::-1]
bolhas_visuais = [bolha_cor(r) for r in h_reverso]
num_linhas_ativas = (n_analise + linha_size - 1) // linha_size
for i in range(0, len(bolhas_visuais), linha_size):
    linha = bolhas_visuais[i:i + linha_size]
    is_ativo = i < num_linhas_ativas * linha_size
    estilo = 'font-size:24px;' if is_ativo else 'font-size:20px; opacity:0.5;'
    bolha_html = "".join(f"<span style='{estilo} margin-right:4px;'>{b}</span>" for b in linha)
    st.markdown(f"<div style='display:flex; gap:4px;'>{bolha_html}</div>", unsafe_allow_html=True)

# Painel de análise com métricas
st.subheader(f"📊 Análise das Últimas {n_analise} Jogadas")
valores = get_valores(h, n_analise)
col1, col2, col3 = st.columns(3)
col1.metric("Total Casa (C)", valores.count("C"))
col2.metric("Total Visitante (V)", valores.count("V"))
col3.metric("Total Empates (E)", valores.count("E"))

st.write(f"Maior sequência: **{maior_sequencia(h, n_analise)}**")
st.write(f"Alternância total: **{alternancia(h, n_analise)}**")
st.write(f"Eco visual: **{eco_visual(h, n_analise)}**")
st.write(f"Eco parcial: **{eco_parcial(h, n_analise)}**")
st.write(f"Distância entre últimos empates: **{dist_empates(h, n_analise)}**")
st.write(f"Blocos espelhados: **{blocos_espelhados(h, n_analise)}**")
st.write(f"Alternância por linha: **{alternancia_por_linha(h, linha_size, n_analise)}**")
st.write(f"Tendência final (últimas {tendencia_window}): **{tendencia_final(h, tendencia_window, n_analise)}**")

# Análises avançadas
st.subheader("🔬 Análises Estatísticas Avançadas")
probs = prob_condicional(h, n_analise)
st.write("Probabilidades condicionais (%):")
for key, val in probs.items():
    st.write(f"Após {key}: C={val.get('C', 0):.0f}%, V={val.get('V', 0):.0f}%, E={val.get('E', 0):.0f}%")

st.write(f"Teste de aleatoriedade (Runs Test): **{teste_aleatoriedade(h, n_analise)}**")

# Gráficos
if len(valores) > 0:
    st.subheader("📈 Gráficos")
    df = pd.DataFrame({"Resultado": valores})
    fig, ax = plt.subplots()
    sns.countplot(x="Resultado", data=df, ax=ax, palette={"C": "red", "V": "blue", "E": "yellow"})
    ax.set_title("Distribuição de Resultados")
    st.pyplot(fig)

# Alertas estratégicos
st.subheader("🚨 Alertas Estratégicos")
alertas = []
if sequencia_final(h, n_analise) >= 5 and valores and valores[-1] in ["C", "V"]:
    alertas.append("🟥 Sequência final ativa — possível inversão")
if eco_visual(h, n_analise) == "Detectado":
    alertas.append("🔁 Eco visual detectado — possível repetição")
if eco_parcial(h, n_analise).startswith(("4", "5", "6")):
    alertas.append("🧠 Eco parcial — padrão reescrito com semelhança")
if isinstance(dist_empates(h, n_analise), int) and dist_empates(h, n_analise) == 1:
    alertas.append("🟨 Empates consecutivos — instabilidade")
if blocos_espelhados(h, n_analise) >= 1:
    alertas.append("🧩 Bloco espelhado — reflexo estratégico")

if not alertas:
    st.info("Nenhum padrão crítico identificado.")
else:
    for alerta in alertas:
        st.warning(alerta)
