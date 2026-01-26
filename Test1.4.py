import streamlit as st

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Football Studio – AI FINAL",
    layout="wide"
)

# =====================================================
# STATE
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "cycle_memory" not in st.session_state:
    st.session_state.cycle_memory = []

# =====================================================
# UI
# =====================================================
st.title("⚽ Football Studio – AI FINAL (Baixo Erro)")

c1, c2, c3, c4 = st.columns(4)
if c1.button("🔴 Home"):
    st.session_state.history.insert(0, "🔴")
if c2.button("🔵 Away"):
    st.session_state.history.insert(0, "🔵")
if c3.button("🟡 Draw"):
    st.session_state.history.insert(0, "🟡")
if c4.button("Reset"):
    st.session_state.history.clear()
    st.session_state.cycle_memory.clear()

# =====================================================
# HISTÓRICO 9x10
# =====================================================
st.divider()
st.subheader("📊 Histórico (Mais recente → Mais antigo)")

def render_history(hist):
    rows = [hist[i:i+9] for i in range(0, len(hist), 9)]
    for row in rows[:10]:
        st.write(" ".join(row))

render_history(st.session_state.history)

# =====================================================
# BLOCO ATIVO
# =====================================================
def get_active_block(history):
    if not history:
        return None, 0

    base = history[0]
    size = 1
    for i in range(1, len(history)):
        if history[i] == base:
            size += 1
        else:
            break
    return base, size

# =====================================================
# CICLOS (TIPO DE MESA)
# =====================================================
def classify_block(size):
    if size == 1:
        return "CHOPPY"
    if size == 2:
        return "CURTO"
    if size == 3:
        return "STREAK"
    if size >= 4:
        return "STREAK_FORTE"

def update_cycle(block_type):
    mem = st.session_state.cycle_memory
    if not mem or mem[-1] != block_type:
        mem.append(block_type)
    if len(mem) > 3:
        mem[:] = mem[-3:]

# =====================================================
# ANÁLISE FINAL (RESOLVE O ERRO)
# =====================================================
def analyze(history):
    if len(history) < 3:
        return "INÍCIO", "WAIT", 0, "SEM LEITURA"

    color, size = get_active_block(history)
    prev = history[1]

    # -------- EMPATE --------
    if color == "🟡":
        return "RESET", "WAIT", 0, "EMPATE TRAVA MESA"

    block_type = classify_block(size)
    update_cycle(block_type)

    mem = st.session_state.cycle_memory

    # -------- FILTRO DE MATURAÇÃO --------
    if size < 3:
        return "FORMAÇÃO", "WAIT", 0, "BLOCO AINDA NÃO PAGA"

    # -------- FILTRO DE SATURAÇÃO --------
    if mem.count("STREAK_FORTE") >= 2:
        return "SATURAÇÃO", "WAIT", 0, "CICLO REPETIDO"

    # -------- FILTRO DE ARMADILHA --------
    if size == 3 and prev != color and prev != "🟡":
        return "ARMADILHA", "WAIT", 0, "STREAK CURTA SUSPEITA"

    # -------- ENTRADA VÁLIDA --------
    confidence = 60 + min(size * 3, 12)

    return (
        f"CONTINUIDADE {color}",
        color,
        confidence,
        f"{block_type} MATURADO"
    )

# =====================================================
# OUTPUT
# =====================================================
context, suggestion, conf, reading = analyze(st.session_state.history)

st.divider()
st.subheader("🧠 Análise")

c1, c2, c3 = st.columns(3)
c1.metric("Contexto", context)
c2.metric("Confiança", f"{conf}%")
c3.metric("Ciclo", " → ".join(st.session_state.cycle_memory))

st.info(f"📌 Leitura: {reading}")

st.subheader("🎯 Decisão")
if suggestion in ["🔴", "🔵"]:
    st.success(f"ENTRADA SUGERIDA: {suggestion} ({conf}%)")
else:
    st.warning("AGUARDAR – proteção de banca ativa")

st.caption(
    "Sistema final: bloco ativo + maturação + memória de ciclo + freio de saturação. "
    "Menos entradas, muito menos erro."
)
