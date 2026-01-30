import streamlit as st
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt

# ================= CONFIG =================
st.set_page_config(
    page_title="Football Studio Pro — Leitura Correta",
    layout="wide"
)

# ================= AVISO =================
st.sidebar.markdown("""
### ⚠️ Aviso
Ferramenta analítica e educacional.  
Sem garantia de ganhos.
""")

# ================= STATE =================
if "historico" not in st.session_state:
    st.session_state.historico = []

# ================= INPUT =================
def adicionar_resultado(v):
    if v in ["C", "V", "E", "🔽"]:
        st.session_state.historico.append(v)

# ================= BASE CORRETA =================
def historico_visual(h):
    """Mais recente → mais antigo (esquerda → direita)"""
    return list(reversed(h))

def leitura_analise(h, n=27):
    """
    Leitura correta do tempo:
    Direita → esquerda
    Mais antigo → mais recente
    """
    validos = [x for x in h if x in ["C", "V", "E"]]
    return validos[-n:]

# ================= CICLOS =================
def ciclos_9(h):
    h = leitura_analise(h, 81)
    ciclos = []
    for i in range(0, len(h), 9):
        bloco = h[i:i+9]
        if len(bloco) == 9:
            ciclos.append(bloco)
    return ciclos[::-1]  # ciclo atual primeiro

# ================= MÉTRICAS =================
def sequencia_final(h):
    h = leitura_analise(h, 27)
    if not h:
        return 0
    base = h[-1]
    count = 1
    for i in range(len(h)-2, -1, -1):
        if h[i] == base:
            count += 1
        else:
            break
    return count

def alternancia(h):
    h = leitura_analise(h, 27)
    return sum(1 for i in range(1, len(h)) if h[i] != h[i-1])

def eco_ciclo(ciclos):
    if len(ciclos) < 2:
        return "Poucos ciclos"
    return "Detectado" if ciclos[0] == ciclos[1] else "Não houve"

def quebra_ciclo(ciclos):
    if len(ciclos) < 2:
        return "N/A"
    iguais = sum(1 for a, b in zip(ciclos[0], ciclos[1]) if a == b)
    return f"{iguais}/9 semelhantes"

def tendencia_ciclo(ciclo):
    return {
        "C": ciclo.count("C"),
        "V": ciclo.count("V"),
        "E": ciclo.count("E")
    }

def bolha(r):
    return {"C":"🟥","V":"🟦","E":"🟨","🔽":"⬇️"}.get(r,"⬜")

# ================= UI =================
st.title("🎲 Football Studio Pro — Leitura Temporal Correta")

# ===== SIDEBAR =====
with st.sidebar:
    if st.button("🧹 Limpar histórico"):
        st.session_state.historico = []
        st.rerun()

    st.download_button(
        "📥 Baixar histórico",
        json.dumps(st.session_state.historico),
        "historico.json"
    )

    up = st.file_uploader("📤 Carregar histórico", ["json"])
    if up:
        data = json.load(up)
        st.session_state.historico.extend(
            [x for x in data if x in ["C","V","E","🔽"]]
        )
        st.rerun()

# ===== ENTRADA =====
st.subheader("Entrada Manual")
c1,c2,c3,c4 = st.columns(4)
if c1.button("Casa"): adicionar_resultado("C")
if c2.button("Visitante"): adicionar_resultado("V")
if c3.button("Empate"): adicionar_resultado("E")
if c4.button("Novo Baralho"): adicionar_resultado("🔽")

if st.button("↩️ Desfazer") and st.session_state.historico:
    st.session_state.historico.pop()
    st.rerun()

# ===== HISTÓRICO VISUAL =====
st.subheader("🧾 Histórico (mais recente → mais antigo)")
hist_vis = historico_visual(st.session_state.historico)

for i in range(0, len(hist_vis), 9):
    st.markdown(" ".join(bolha(x) for x in hist_vis[i:i+9]))

# ===== ANÁLISE =====
st.subheader("📊 Leitura Analítica (tempo correto)")
ciclos = ciclos_9(st.session_state.historico)

if ciclos:
    atual = ciclos[0]
    st.write("Sequência final:", sequencia_final(st.session_state.historico))
    st.write("Alternância:", alternancia(st.session_state.historico))
    st.write("Eco de ciclo:", eco_ciclo(ciclos))
    st.write("Quebra de ciclo:", quebra_ciclo(ciclos))
    st.write("Tendência do ciclo atual:", tendencia_ciclo(atual))

    st.subheader("🔁 Ciclo Atual (9)")
    st.markdown(" ".join(bolha(x) for x in atual[::-1]))

# ===== GRÁFICO =====
val = leitura_analise(st.session_state.historico, 27)
if val:
    st.subheader("📈 Distribuição")
    pd.Series(val).value_counts().plot(kind="bar")
    st.pyplot(plt.gcf())
