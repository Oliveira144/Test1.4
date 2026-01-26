import streamlit as st
from collections import deque, Counter

=========================================================

FOOTBALL STUDIO AI – APP COMPLETO, ESTÁVEL E CORRIGIDO

=========================================================

st.set_page_config( page_title="Football Studio AI – Verdadeiro e Completo", layout="wide" )

================= CONFIGURAÇÕES ==========================

MAX_HISTORY = 90          # 9 colunas x 10 linhas WINDOW_ALT = 6            # alternância WINDOW_PATTERN = 12       # padrões gerais

================= ESTADO ================================

if "history" not in st.session_state: st.session_state.history = deque(maxlen=MAX_HISTORY)

================= FUNÇÕES DE ANÁLISE ====================

def clean_history(seq): return [x for x in seq if x != '🟡']

def detect_alternance(history): if len(history) < WINDOW_ALT: return {"status": "Insuficiente", "confidence": 0}

seq = list(history)[-WINDOW_ALT:]
clean = clean_history(seq)

if len(clean) < 4:
    return {"status": "Ruído", "confidence": 0}

alternations = sum(clean[i] != clean[i+1] for i in range(len(clean)-1))
score = alternations / (len(clean)-1)

if score >= 0.85:
    return {"status": "Alternância Limpa", "confidence": round(score*100,1)}
if score >= 0.65:
    return {"status": "Alternância com Ruído", "confidence": round(score*100,1)}
if score >= 0.45:
    return {"status": "Falsa Alternância", "confidence": round(score*100,1)}
return {"status": "Sem Alternância", "confidence": round(score*100,1)}

def detect_repetition(history): if len(history) < 2: return "Nenhuma"

last = history[-1]
count = 1
for i in range(len(history)-2, -1, -1):
    if history[i] == last:
        count += 1
    else:
        break
return f"{count}x {last}" if count > 1 else "Nenhuma"

def detect_pattern(history): if len(history) < 6: return "Dados insuficientes"

seq = list(history)[-WINDOW_PATTERN:]
clean = clean_history(seq)

# Empate como âncora
if seq.count('🟡') >= 2:
    return "Empate como âncora de manipulação"

# Alternância estrutural
if len(clean) >= 4 and all(clean[i] != clean[i+1] for i in range(len(clean)-1)):
    return "Alternância estrutural"

# Bloco dominante
counts = Counter(clean)
dom, qty = counts.most_common(1)[0]
if qty >= 4:
    return f"Bloco dominante {dom}"

# Reversão clara
if len(clean) >= 4 and clean[-1] != clean[-2] and clean[-2] == clean[-3]:
    return "Reversão de padrão"

return "Padrão misto / camuflado"

def detect_manipulation_level(alt, pattern, rep): if alt == "Alternância Limpa": return 1 if alt == "Alternância com Ruído": return 3 if "Bloco" in pattern: return 4 if pattern == "Reversão de padrão": return 6 if alt == "Falsa Alternância": return 7 if "camuflado" in pattern: return 8 return 5

def detect_breach(alt_status, confidence): return alt_status == "Alternância Limpa" and confidence >= 80

def predict_next(history, alt_status, confidence, pattern): if len(history) < 3: return "Sem previsão", 0

last = history[-1]

if alt_status in ["Alternância Limpa", "Alternância com Ruído"]:
    return ('🔵' if last == '🔴' else '🔴'), confidence

if "Bloco dominante" in pattern:
    return last, 60

return "Aguardar", 0

================= INTERFACE ==============================

st.title("🧠 Football Studio – Sistema Verdadeiro e Completo")

col1, col2, col3, col4 = st.columns(4) with col1: if st.button("🔴 Casa"): st.session_state.history.append('🔴') with col2: if st.button("🔵 Visitante"): st.session_state.history.append('🔵') with col3: if st.button("🟡 Empate"): st.session_state.history.append('🟡') with col4: if st.button("🔄 Reset"): st.session_state.history.clear()

st.divider()

================= HISTÓRICO ==============================

hist = list(st.session_state.history) rows = [hist[i:i+9] for i in range(0, len(hist), 9)]

st.subheader("📜 Histórico 9x10") for row in rows[-10:]: st.write(" ".join(row))

================= ANÁLISE ================================

alt = detect_alternance(hist) pattern = detect_pattern(hist) rep = detect_repetition(hist) manip_level = detect_manipulation_level(alt['status'], pattern, rep) breach = detect_breach(alt['status'], alt['confidence']) pred, conf = predict_next(hist, alt['status'], alt['confidence'], pattern)

st.divider()

st.subheader("📊 Painel Estratégico") colA, colB, colC, colD, colE = st.columns(5) with colA: st.metric("Alternância", alt['status']) with colB: st.metric("Confiança", f"{alt['confidence']}%") with colC: st.metric("Repetição", rep) with colD: st.metric("Nível Manipulação", manip_level) with colE: st.metric("Brecha", "SIM" if breach else "NÃO")

st.subheader("🧩 Padrão Detectado") st.info(pattern)

st.subheader("🎯 Decisão") if breach: st.success(f"BRECHA → Entrada sugerida: {pred} ({conf}%)") elif pred != "Aguardar": st.warning(f"Possível leitura: {pred} ({conf}%)") else: st.info("Aguardar – sem vantagem estatística")

st.caption("Versão estável: leitura real de alternância, bloco, reversão, empate âncora, brechas e níveis de manipulação")
