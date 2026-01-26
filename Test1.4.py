import streamlit as st
from collections import deque, Counter

# =========================================================
# FOOTBALL STUDIO AI - HISTÓRICO CORRETO (ANÁLISE + VISUAL)
# =========================================================

st.set_page_config(
    page_title="Football Studio AI - Complete",
    layout="wide"
)

# ================= CONFIG =================
MAX_HISTORY = 90
WINDOW_ALT = 6
WINDOW_PATTERN = 12

# ================= STATE ==================
if "history" not in st.session_state:
    # INTERNO: sempre mais antigo -> mais recente
    st.session_state.history = deque(maxlen=MAX_HISTORY)

# ================= CORE UTILITIES =========
def remove_draws(seq):
    return [x for x in seq if x != "🟡"]

def get_last_non_draw(history):
    # history: antigo -> recente
    for x in reversed(history):
        if x != "🟡":
            return x
    return None

# ================= ANALYSIS ===============
def detect_alternance(history):
    if len(history) < WINDOW_ALT:
        return {"status": "Insufficient", "confidence": 0}

    window = list(history)[-WINDOW_ALT:]  # últimos eventos (recentes)
    clean = remove_draws(window)

    if len(clean) < 4:
        return {"status": "Noise", "confidence": 0}

    changes = sum(clean[i] != clean[i + 1] for i in range(len(clean) - 1))
    score = changes / (len(clean) - 1)

    if score >= 0.85:
        return {"status": "Clean Alternance", "confidence": int(score * 100)}
    elif score >= 0.65:
        return {"status": "Noisy Alternance", "confidence": int(score * 100)}
    elif score >= 0.45:
        return {"status": "False Alternance", "confidence": int(score * 100)}
    else:
        return {"status": "No Alternance", "confidence": int(score * 100)}

def detect_repetition(history):
    last = get_last_non_draw(history)
    if last is None:
        return "None (only draws)"

    count = 1
    for item in reversed(list(history)[:-1]):
        if item == "🟡":
            continue
        if item == last:
            count += 1
        else:
            break

    return f"{count}x {last}" if count > 1 else "None"

def detect_pattern(history):
    if len(history) < 6:
        return "Insufficient data"

    window = list(history)[-WINDOW_PATTERN:]
    clean = remove_draws(window)

    if window.count("🟡") >= 2:
        return "Draw as manipulation anchor"

    if len(clean) >= 4 and all(clean[i] != clean[i + 1] for i in range(len(clean) - 1)):
        return "Structural alternance"

    counts = Counter(clean)
    if counts:
        dominant, qty = counts.most_common(1)[0]
        if qty >= 4:
            return f"Dominant block {dominant}"

    if len(clean) >= 4 and clean[-1] != clean[-2] and clean[-2] == clean[-3]:
        return "Pattern reversal"

    return "Camouflaged / mixed pattern"

def detect_manipulation_level(alt_status, pattern):
    if alt_status == "Clean Alternance":
        return 1
    if alt_status == "Noisy Alternance":
        return 3
    if "Dominant block" in pattern:
        return 4
    if pattern == "Pattern reversal":
        return 6
    if alt_status == "False Alternance":
        return 7
    if "Camouflaged" in pattern:
        return 8
    return 5

def detect_breach(alt_status, confidence, pattern):
    return (
        alt_status == "Clean Alternance"
        and confidence >= 80
        and "Camouflaged" not in pattern
    )

def predict_next(history, alt_status, confidence, pattern):
    last = get_last_non_draw(history)
    if last is None or len(history) < 3:
        return "WAIT", 0

    if alt_status in ("Clean Alternance", "Noisy Alternance"):
        return ("🔵" if last == "🔴" else "🔴"), confidence

    if "Dominant block" in pattern:
        dominant = pattern.split()[-1]
        return dominant, 60

    return "WAIT", 0

# ================= UI ======================
st.title("Football Studio AI - Complete Analysis System")

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("🔴 Home"):
        st.session_state.history.append("🔴")
with c2:
    if st.button("🔵 Away"):
        st.session_state.history.append("🔵")
with c3:
    if st.button("🟡 Draw"):
        st.session_state.history.append("🟡")
with c4:
    if st.button("Reset"):
        st.session_state.history.clear()

st.divider()

# ================= HISTORY (VISUAL CORRETO) =================
hist_internal = list(st.session_state.history)     # antigo -> recente
hist_display = hist_internal[::-1]                 # recente -> antigo

rows = [hist_display[i:i + 9] for i in range(0, len(hist_display), 9)]

st.subheader("History (9x10 – mais recente à esquerda)")
for row in rows[:10]:
    st.write(" ".join(row))

# ================= ANALYSIS PANEL ==========
alt = detect_alternance(hist_internal)
pattern = detect_pattern(hist_internal)
rep = detect_repetition(hist_internal)
level = detect_manipulation_level(alt["status"], pattern)
breach = detect_breach(alt["status"], alt["confidence"], pattern)
prediction, conf = predict_next(
    hist_internal,
    alt["status"],
    alt["confidence"],
    pattern
)

st.divider()

st.subheader("Analysis Panel")
a, b, c, d, e = st.columns(5)
a.metric("Alternance", alt["status"])
b.metric("Confidence", f"{alt['confidence']}%")
c.metric("Repetition", rep)
d.metric("Manipulation Level", level)
e.metric("Breach", "YES" if breach else "NO")

st.subheader("Detected Pattern")
st.info(pattern)

st.subheader("Decision")
if breach:
    st.success(f"ENTRY SUGGESTED: {prediction} ({conf}%)")
elif prediction != "WAIT":
    st.warning(f"Possible path: {prediction} ({conf}%)")
else:
    st.info("WAIT - No statistical advantage")

st.caption(
    "Versão estável. Histórico interno preservado | Exibição corrigida "
    "| Alternância, blocos, reversão, draw anchor e brechas ativas."
)
