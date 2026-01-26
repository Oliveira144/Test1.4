import streamlit as st from collections
import deque, Counter

st.set_page_config(page_title="Football Studio AI – Completo + Atualizado", layout="wide")

================= CONFIG =================

MAX_HISTORY = 90   # 9 colunas x 10 linhas WINDOW_ALT = 6     # alternância WINDOW_PATTERN = 12

================= STATE ==================

if "history" not in st.session_state: st.session_state.history = deque(maxlen=MAX_HISTORY)

================= CORE LOGIC ==============

def detect_alternance(history, window=WINDOW_ALT): if len(history) < window: return {"status": "Insuficiente", "confidence": 0}

seq = list(history)[-window:]
pairs = []
for i in range(len(seq)-1):
    if seq[i] != '🟡' and seq[i+1] != '🟡':
        pairs.append(seq[i] != seq[i+1])

if not pairs:
    return {"status": "Ruído", "confidence": 0}

score = sum(pairs) / len(pairs)

if score >= 0.85:
    status = "Alternância Limpa"
elif score >= 0.65:
    status = "Alternância com Ruído"
elif score >= 0.45:
    status = "Falsa Alternância"
else:
    status = "Sem Alternância"

return {"status": status, "confidence": round(score*100, 1)}

def detect_repetition(history): if len(history) < 2: return "Nenhuma" last = history[-1] count = 1 for i in range(len(history)-2, -1, -1): if history[i] == last: count += 1 else: break return f"{count}x {last}" if count > 1 else "Nenhuma"

def detect_pattern(history, window=WINDOW_PATTERN): # Detecta múltiplos padrões além de tendência simples if len(history) < 6: return "Dados insuficientes"

seq = list(history)[-window:]

# Remove empates para leitura estrutural
clean = [x for x in seq if x != '🟡']

# Alternância curta
if len(clean) >= 4 and all(clean[i] != clean[i+1] for i in range(len(clean)-1)):
    return "Alternância estrutural"

# Bloco / repetição estendida
counts = Counter(clean)
dominant = counts.most_common(1)[0]
if dominant[1] >= 4:
    return f"Bloco dominante {dominant[0]}"

# Reversão (ex: 🔴🔴🔴🔵)
if len(clean) >= 4 and clean[-1] != clean[-2] and clean[-2] == clean[-3]:
    return "Reversão de padrão"

# Empate como âncora
if seq.count('🟡') >= 2:
    return "Empate como âncora de manipulação"

return "Padrão misto / camuflado"(history, window=WINDOW_PATTERN):
if len(history) < window:
    return "Dados insuficientes"
seq = list(history)[-window:]
counts = Counter(seq)
dominant = counts.most_common(1)[0]
if dominant[1] / window > 0.6:
    return f"Tendência dominante {dominant[0]}"
return "Padrão misto / camuflado"

def detect_manipulation_level(history): alt = detect_alternance(history) rep = detect_repetition(history)

# Níveis 1–9 (base estratégica)
if alt['status'] == "Alternância Limpa":
    return 1
if alt['status'] == "Alternância com Ruído":
    return 3
if "3x" in rep:
    return 4
if alt['status'] == "Falsa Alternância":
    return 7
if detect_pattern(history).startswith("Padrão misto"):
    return 8
return 5

def detect_breach(history): if len(history) < 7: return False alt = detect_alternance(history) if alt['status'] == "Alternância Limpa" and alt['confidence'] > 80: return True return False

def predict_next(history): if len(history) < 3: return "Sem previsão", 0

alt = detect_alternance(history)
last = history[-1]

if alt['status'] in ["Alternância Limpa", "Alternância com Ruído"]:
    return ('🔵' if last == '🔴' else '🔴'), alt['confidence']

counts = Counter(history[-6:])
guess = counts.most_common(1)[0][0]
return guess, 55

================= UI ======================

st.title("🧠 Football Studio – Sistema Completo de Leitura e Previsão")

col1, col2, col3, col4 = st.columns(4) with col1: if st.button("🔴 Casa"): st.session_state.history.append('🔴') with col2: if st.button("🔵 Visitante"): st.session_state.history.append('🔵') with col3: if st.button("🟡 Empate"): st.session_state.history.append('🟡') with col4: if st.button("🔄 Reset"): st.session_state.history.clear()

st.divider()

================= HISTORY =================

hist = list(st.session_state.history) rows = [hist[i:i+9] for i in range(0, len(hist), 9)]

st.subheader("📜 Histórico 9x10") for row in rows[-10:]: st.write(" ".join(row))

================= ANALYSIS =================

alt = detect_alternance(hist) rep = detect_repetition(hist) pattern = detect_pattern(hist) manip_level = detect_manipulation_level(hist) breach = detect_breach(hist) pred, conf = predict_next(hist)

st.divider()

st.subheader("📊 Painel Estratégico") colA, colB, colC, colD, colE = st.columns(5) with colA: st.metric("Alternância", alt['status']) with colB: st.metric("Confiança", f"{alt['confidence']}%") with colC: st.metric("Repetição", rep) with colD: st.metric("Nível Manipulação", manip_level) with colE: st.metric("Brecha", "SIM" if breach else "NÃO")

st.subheader("🧩 Leitura do Cenário") st.info(pattern)

st.subheader("🎯 Previsão / Ação") if breach and conf >= 70: st.success(f"BRECHA DETECTADA → Entrada sugerida: {pred} ({conf}%)") elif conf >= 60: st.warning(f"Possível caminho: {pred} ({conf}%)") else: st.info("Momento de espera – padrão instável")

st.caption("Sistema completo: histórico 9x10, alternância relacional, repetição, padrão, brechas, previsão e níveis de manipulação")
