import streamlit as st
from collections import deque, Counter

# =========================================================
# FOOTBALL STUDIO AI - CORRIGIDO E MELHORADO (2025)
# =========================================================

st.set_page_config(
    page_title="Football Studio AI - Versão Corrigida",
    layout="wide"
)

# ================= CONFIG =================
MAX_HISTORY = 90          # 9 colunas x 10 linhas
WINDOW_ALT = 8            # aumentei um pouco para mais confiabilidade
WINDOW_PATTERN = 12

# ================= STATE ==================
if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=MAX_HISTORY)

# ================= UTILITÁRIOS ============
def remove_draws(seq):
    return [x for x in seq if x != "🟡"]

def get_last_non_draw(history):
    """Retorna o último resultado que NÃO foi draw, ou None"""
    for item in reversed(list(history)):
        if item != "🟡":
            return item
    return None

# ================= ANÁLISES ===============
def detect_alternance(history):
    if len(history) < WINDOW_ALT:
        return {"status": "Dados insuficientes", "confidence": 0, "changes": 0, "total": 0}

    window = list(history)[-WINDOW_ALT:]
    clean = remove_draws(window)

    if len(clean) < 4:
        return {"status": "Poucos resultados válidos", "confidence": 0, "changes": 0, "total": 0}

    changes = sum(clean[i] != clean[i + 1] for i in range(len(clean) - 1))
    total_transitions = len(clean) - 1
    score = changes / total_transitions if total_transitions > 0 else 0

    if score >= 0.85:
        status = "Alternância Limpa"
    elif score >= 0.65:
        status = "Alternância com Ruído"
    elif score >= 0.40:
        status = "Alternância Fraca / Falsa"
    else:
        status = "Sem Alternância"

    return {
        "status": status,
        "confidence": int(score * 100),
        "changes": changes,
        "total": total_transitions
    }

def detect_repetition(history):
    if len(history) < 2:
        return "Nenhuma"
    
    last_non_draw = get_last_non_draw(history)
    if last_non_draw is None:
        return "Apenas draws recentes"

    count = 1
    for item in reversed(list(history)[:-1]):
        if item == "🟡":
            continue
        if item == last_non_draw:
            count += 1
        else:
            break

    return f"{count}x {last_non_draw}" if count > 1 else "Nenhuma"

def detect_pattern(history):
    if len(history) < 6:
        return "Dados insuficientes"

    window = list(history)[-WINDOW_PATTERN:]
    clean = remove_draws(window)
    draws_count = window.count("🟡")

    if draws_count >= 4:
        return f"Possível manipulação por draws ({draws_count} em {WINDOW_PATTERN})"

    if len(clean) < 4:
        return "Poucos resultados válidos para padrão"

    # Alternância perfeita nos últimos clean
    if all(clean[i] != clean[i + 1] for i in range(len(clean) - 1)):
        return "Alternância estrutural forte"

    counts = Counter(clean)
    dominant, qty = counts.most_common(1)[0]

    # Verifica se é bloco consecutivo (melhor que só contagem total)
    max_consecutive = 1
    current = 1
    for i in range(1, len(clean)):
        if clean[i] == clean[i-1]:
            current += 1
            max_consecutive = max(max_consecutive, current)
        else:
            current = 1

    if max_consecutive >= 4 or qty >= 5:
        return f"Bloco dominante {dominant} ({qty}× total, {max_consecutive} consecutivos)"

    # Reversão mais robusta (olha últimos 4 clean)
    if len(clean) >= 4:
        last_four = clean[-4:]
        if (last_four[3] != last_four[2] and 
            last_four[2] == last_four[1] and 
            last_four[1] == last_four[0]):
            return "Reversão de padrão (padrão → mudança)"

    return "Padrão misto / camuflado"

def detect_manipulation_level(alt_status, pattern):
    if "Limpa" in alt_status:
        return 1
    if "com Ruído" in alt_status:
        return 3
    if "Bloco dominante" in pattern:
        return 4
    if "Reversão" in pattern:
        return 6
    if "Fraca / Falsa" in alt_status:
        return 7
    if "camuflado" in pattern.lower() or "misto" in pattern.lower():
        return 8
    if "draws" in pattern.lower():
        return 9
    return 5

def detect_breach(alt_status, confidence, pattern):
    return (
        "Limpa" in alt_status
        and confidence >= 82
        and "camuflado" not in pattern.lower()
        and "draws" not in pattern.lower()
    )

def predict_next(history, alt_status, confidence, pattern):
    last_non_draw = get_last_non_draw(history)
    if last_non_draw is None or len(history) < 4:
        return "AGUARDE", 0, "Histórico insuficiente ou só draws"

    if "Limpa" in alt_status and confidence >= 70:
        prediction = "🔵" if last_non_draw == "🔴" else "🔴"
        return prediction, confidence, "Baseado em alternância forte"

    if "com Ruído" in alt_status and confidence >= 65:
        prediction = "🔵" if last_non_draw == "🔴" else "🔴"
        return prediction, confidence - 15, "Baseado em alternância moderada"

    if "Bloco dominante" in pattern:
        # Extrai o dominante do texto do pattern
        if "🔴" in pattern:
            return "🔴", 68, "Continuação de bloco dominante 🔴"
        if "🔵" in pattern:
            return "🔵", 68, "Continuação de bloco dominante 🔵"

    if "Reversão" in pattern:
        prediction = "🔵" if last_non_draw == "🔴" else "🔴"
        return prediction, 62, "Após reversão detectada"

    return "AGUARDE", 0, "Sem vantagem estatística clara"

# ================= INTERFACE ===============
st.title("Football Studio AI – Versão Corrigida")

cols = st.columns(4)
with cols[0]:
    if st.button("🔴 Home", use_container_width=True):
        st.session_state.history.append("🔴")
with cols[1]:
    if st.button("🔵 Away", use_container_width=True):
        st.session_state.history.append("🔵")
with cols[2]:
    if st.button("🟡 Draw", use_container_width=True):
        st.session_state.history.append("🟡")
with cols[3]:
    if st.button("Resetar Tudo", type="primary", use_container_width=True):
        st.session_state.history.clear()
        st.rerun()

st.divider()

# Histórico visual
hist_list = list(st.session_state.history)
rows = [hist_list[i:i+9] for i in range(0, len(hist_list), 9)]

st.subheader(f"Histórico ({len(hist_list)} entradas – 9 × {len(rows)})")
for row in rows[-10:]:  # últimas 10 linhas
    st.write("  ".join(row if row else ["—"]*9))

# Análises
alt = detect_alternance(hist_list)
pattern = detect_pattern(hist_list)
rep = detect_repetition(hist_list)
level = detect_manipulation_level(alt["status"], pattern)
breach = detect_breach(alt["status"], alt["confidence"], pattern)
pred, conf, reason = predict_next(hist_list, alt["status"], alt["confidence"], pattern)

st.divider()

st.subheader("Painel de Análise")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Alternância", alt["status"])
col2.metric("Confiança", f"{alt['confidence']}%")
col3.metric("Repetição", rep)
col4.metric("Nível Manipulação", level)
col5.metric("Breach / Oportunidade", "SIM" if breach else "Não")

st.subheader("Padrão Detectado")
st.info(pattern)

st.subheader("Decisão / Sugestão")
if breach:
    st.success(f"**ENTRADA RECOMENDADA**: {pred}  ({conf}%)\n\n{reason}")
elif pred != "AGUARDE":
    st.warning(f"**Caminho possível**: {pred}  ({conf}%)\n\n{reason}")
else:
    st.info(f"**AGUARDE** – sem vantagem clara\n\n{reason}")

st.caption("Versão corrigida: previsão respeita último non-draw • blocos consecutivos • reversão mais inteligente • draws tratados com mais cuidado")
