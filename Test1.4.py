import streamlit as st

# =====================================================
# CONFIGURAÇÃO
# =====================================================
st.set_page_config(
    page_title="Football Studio – Leitura Real",
    layout="wide"
)

# =====================================================
# ESTADO
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = []

# =====================================================
# UI – ENTRADAS
# =====================================================
st.title("⚽ Football Studio – Leitura Real de Mesa Física")

c1, c2, c3, c4 = st.columns(4)
if c1.button("🔴 Home"):
    st.session_state.history.insert(0, "🔴")
if c2.button("🔵 Away"):
    st.session_state.history.insert(0, "🔵")
if c3.button("🟡 Draw"):
    st.session_state.history.insert(0, "🟡")
if c4.button("Reset"):
    st.session_state.history.clear()

# =====================================================
# HISTÓRICO 9x10 (RECENTE → ANTIGO)
# =====================================================
st.divider()
st.subheader("📊 Histórico (Mais recente → Mais antigo)")

def render_history(hist):
    rows = [hist[i:i+9] for i in range(0, len(hist), 9)]
    for row in rows[:10]:
        st.write(" ".join(row))

render_history(st.session_state.history)

# =====================================================
# LEITURA – BLOCO ATIVO
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
# ANÁLISE COMPLETA (CORRIGIDA)
# =====================================================
def analyze_table(history):
    if len(history) < 2:
        return {
            "context": "INÍCIO DE MESA",
            "reading": "Sem leitura ainda",
            "suggestion": "WAIT",
            "confidence": 0,
            "level": "NEUTRO"
        }

    block_color, block_size = get_active_block(history)
    prev = history[1]

    # ---------------- EMPATE ----------------
    if block_color == "🟡":
        return {
            "context": "RESET / ATRASO",
            "reading": "Empate usado para travar fluxo",
            "suggestion": "WAIT",
            "confidence": 0,
            "level": "CONTROLE"
        }

    # ---------------- CONTINUIDADE FORTE ----------------
    if block_size >= 4:
        return {
            "context": f"CONTINUIDADE FORTE {block_color}",
            "reading": "Bloco dominante ativo",
            "suggestion": block_color,
            "confidence": min(60 + block_size * 4, 78),
            "level": "BAIXO RISCO"
        }

    # ---------------- CONTINUIDADE ----------------
    if block_size == 3:
        return {
            "context": f"CONTINUIDADE {block_color}",
            "reading": "Fluxo ainda saudável",
            "suggestion": block_color,
            "confidence": 62,
            "level": "MODERADO"
        }

    # ---------------- BLOCO EM FORMAÇÃO ----------------
    if block_size == 2:
        return {
            "context": f"BLOCO EM FORMAÇÃO {block_color}",
            "reading": "Definição de lado",
            "suggestion": block_color,
            "confidence": 58,
            "level": "MODERADO"
        }

    # ---------------- BLOCO UNITÁRIO ----------------
    if block_size == 1:
        if prev != "🟡" and prev != block_color:
            return {
                "context": "RESPIRO / ARMADILHA",
                "reading": "Quebra curta sem confirmação",
                "suggestion": prev,
                "confidence": 52,
                "level": "ALTO RISCO"
            }

        return {
            "context": "INDECISÃO",
            "reading": "Mesa serrilhada / choppy",
            "suggestion": "WAIT",
            "confidence": 0,
            "level": "ALTO RISCO"
        }

# =====================================================
# PAINEL DE ANÁLISE
# =====================================================
analysis = analyze_table(st.session_state.history)

st.divider()
st.subheader("🧠 Análise da Mesa")

c1, c2, c3 = st.columns(3)
c1.metric("Contexto", analysis["context"])
c2.metric("Nível da Mesa", analysis["level"])
c3.metric("Confiança", f"{analysis['confidence']}%")

st.info(f"📌 Leitura: {analysis['reading']}")

# =====================================================
# DECISÃO
# =====================================================
st.subheader("🎯 Decisão")

if analysis["suggestion"] in ["🔴", "🔵"]:
    st.success(
        f"ENTRADA SUGERIDA: {analysis['suggestion']} "
        f"({analysis['confidence']}%)"
    )
else:
    st.warning("AGUARDAR – mesa sem vantagem clara")

st.caption(
    "Leitura real de Football Studio: "
    "mais recente à esquerda, análise por bloco ativo, "
    "empate como reset e leitura sempre para mais."
)
