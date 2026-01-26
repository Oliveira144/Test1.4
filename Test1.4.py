import streamlit as st
from collections import deque

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(
    page_title="Football Studio – FUSION ENGINE",
    layout="wide"
)

# =====================================================
# STATE
# =====================================================
if "history" not in st.session_state:
    st.session_state.history = deque(maxlen=120)  # recente -> antigo

if "cycle_memory" not in st.session_state:
    st.session_state.cycle_memory = []

if "rounds_without_draw" not in st.session_state:
    st.session_state.rounds_without_draw = 0

# =====================================================
# UI
# =====================================================
st.title("⚽ Football Studio – FUSION ENGINE")

c1, c2, c3, c4 = st.columns(4)
if c1.button("🔴 Home"):
    st.session_state.history.appendleft("R")
if c2.button("🔵 Away"):
    st.session_state.history.appendleft("B")
if c3.button("🟡 Draw"):
    st.session_state.history.appendleft("D")
if c4.button("Reset"):
    st.session_state.history.clear()
    st.session_state.cycle_memory.clear()
    st.session_state.rounds_without_draw = 0

# =====================================================
# DRAW COUNTER
# =====================================================
if st.session_state.history:
    if st.session_state.history[0] == "D":
        st.session_state.rounds_without_draw = 0
    else:
        st.session_state.rounds_without_draw += 1

# =====================================================
# HISTORY VIEW
# =====================================================
st.subheader("📊 Histórico (Recente → Antigo)")

def icon(x):
    return "🔴" if x == "R" else "🔵" if x == "B" else "🟡"

st.write(" ".join(icon(x) for x in list(st.session_state.history)[:45]))

# =====================================================
# BLOCK EXTRACTION
# =====================================================
def extract_blocks(hist):
    if not hist:
        return []

    blocks = []
    cur = hist[0]
    size = 1

    for i in range(1, len(hist)):
        if hist[i] == cur:
            size += 1
        else:
            blocks.append({"color": cur, "size": size})
            cur = hist[i]
            size = 1

    blocks.append({"color": cur, "size": size})

    for b in blocks:
        if b["color"] == "D":
            b["type"] = "DRAW"
        elif b["size"] == 1:
            b["type"] = "CHOPPY"
        elif b["size"] == 2:
            b["type"] = "DUPLO"
        elif b["size"] == 3:
            b["type"] = "TRIPLO"
        elif b["size"] >= 6:
            b["type"] = "STREAK FORTE"
        elif b["size"] >= 4:
            b["type"] = "STREAK"
        else:
            b["type"] = "DECAIMENTO"

    return blocks

# =====================================================
# CYCLE MEMORY
# =====================================================
def update_cycle_memory(blocks):
    if not blocks:
        return
    t = blocks[0]["type"]
    mem = st.session_state.cycle_memory
    if not mem or mem[-1] != t:
        mem.append(t)
    if len(mem) > 3:
        mem[:] = mem[-3:]

# =====================================================
# PATTERN ENGINE (ACUMULATIVO)
# =====================================================
def detect_patterns(blocks):
    signals = []
    if not blocks:
        return signals

    sizes = [b["size"] for b in blocks]
    colors = [b["color"] for b in blocks]
    types = [b["type"] for b in blocks]

    # --- BASE ---
    if types[0] == "CHOPPY":
        signals.append((colors[0], 12, "CHOPPY"))

    if types[0] in ["STREAK", "STREAK FORTE"]:
        signals.append((colors[0], 10, types[0]))

    # --- ALTERNÂNCIA ---
    if len(colors) >= 4 and all(colors[i] != colors[i+1] for i in range(3)):
        signals.append((colors[0], 14, "ALTERNÂNCIA REAL"))

    # --- COLAPSO ---
    if len(sizes) >= 3 and sizes[:3] == [1, 1, 2]:
        signals.append((colors[2], 16, "COLAPSO ALTERNÂNCIA"))

    # --- SIMETRIA ---
    if len(sizes) >= 6 and sizes[:3] == sizes[3:6]:
        signals.append((colors[0], 15, "SIMETRIA REPETIDA"))

    # --- DRAW ---
    if st.session_state.rounds_without_draw >= 30:
        signals.append(("D", 18, "DRAW HUNTING"))

    if types[0] == "DRAW" and len(types) > 1 and "STREAK" in types[1]:
        signals.append(("D", 20, "DRAW ÂNCORA"))

    return signals

# =====================================================
# FINAL DECISION (NUNCA REDUZ)
# =====================================================
def ia_decision(hist):
    blocks = extract_blocks(hist)
    update_cycle_memory(blocks)
    signals = detect_patterns(blocks)

    if not signals:
        return "⏳ AGUARDAR", 0, "SEM SINAIS"

    score_map = {}
    context = []

    for color, score, name in signals:
        score_map[color] = score_map.get(color, 0) + score
        context.append(name)

    mem = st.session_state.cycle_memory
    if len(mem) == 3 and mem[0] == mem[2]:
        for k in score_map:
            score_map[k] += 5
            context.append("RESSONÂNCIA CICLO")

    color, score = max(score_map.items(), key=lambda x: x[1])

    if score >= 55:
        label = "🔴 HOME" if color == "R" else "🔵 AWAY" if color == "B" else "🟡 DRAW"
        return f"🎯 APOSTAR {label}", score, " | ".join(context)

    return "⏳ AGUARDAR", score, " | ".join(context)

# =====================================================
# OUTPUT
# =====================================================
decision, score, context = ia_decision(list(st.session_state.history))

st.divider()
st.subheader("🎯 DECISÃO DA IA")
st.success(f"{decision}\n\nScore: {score}\n\nContexto: {context}")

with st.expander("🧠 Memória de Ciclos"):
    st.write(st.session_state.cycle_memory)

with st.expander("🟡 Draw Stats"):
    st.write(f"Rodadas sem Draw: {st.session_state.rounds_without_draw}")
