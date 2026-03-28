import streamlit as st
import pandas as pd
from collections import Counter

st.set_page_config(page_title="Student Survival AI", layout="wide")

# ---- PREMIUM STYLE ----
st.markdown("""
<style>
body {background:#020617;color:white;}
.card {
    background: linear-gradient(145deg,#1e293b,#0f172a);
    padding:20px;
    border-radius:20px;
    margin-bottom:15px;
    box-shadow:0 0 20px rgba(0,255,255,0.15);
}
h1, h2, h3 {color:#38bdf8;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 Student Survival AI")
st.caption("Predict • Analyze • Solve Student Problems in Real-Time")

# ---- SESSION ----
if "history" not in st.session_state:
    st.session_state.history = []

# ---- AI FUNCTIONS ----
def analyze(text):
    t = text.lower()
    if "wifi" in t:
        return "Network Issue"
    elif "heat" in t or "hot" in t:
        return "Heat Problem"
    elif "water" in t:
        return "Water Issue"
    elif "electric" in t or "power" in t:
        return "Electrical Issue"
    else:
        return "General Issue"

def solution(issue):
    return {
        "Network Issue": "Switch to hotspot / LAN / restart router",
        "Heat Problem": "Check ventilation or move to cooler area",
        "Water Issue": "Inform maintenance / use backup supply",
        "Electrical Issue": "Check power backup or inform technician",
        "General Issue": "Forward to admin"
    }.get(issue)

def predict(history):
    wifi = sum("wifi" in h.lower() for h in history)
    water = sum("water" in h.lower() for h in history)
    electric = sum("electric" in h.lower() or "power" in h.lower() for h in history)

    alerts = []

    if wifi >= 2:
        alerts.append("🚨 WiFi issues rising! Possible outage")
    if water >= 2:
        alerts.append("🚨 Water shortage risk detected")
    if electric >= 2:
        alerts.append("🚨 Power failure risk detected")

    if alerts:
        return alerts
    return ["✅ System Stable"]

# ---- PAIN INDEX ----
pain_score = min(len(st.session_state.history) * 10, 100)
st.metric("💔 Campus Pain Index", f"{pain_score}/100")

# ---- LAYOUT ----
col1, col2 = st.columns([2,1])

# ---- INPUT PANEL ----
with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🧑 Enter Your Problem")
    text = st.text_area("Describe your issue")

    if st.button("Analyze Problem"):
        if text:
            st.session_state.history.append(text)

            issue = analyze(text)

            st.markdown("### 🧠 AI Analysis")
            st.write(f"Detected Category: **{issue}**")
            st.write("Reason: Keyword + pattern detection")

            st.markdown("### 💡 Suggested Solution")
            st.success(solution(issue))

    st.markdown('</div>', unsafe_allow_html=True)

# ---- SIDE PANEL ----
with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("🚨 AI Alerts")
    alerts = predict(st.session_state.history)
    for a in alerts:
        st.warning(a)

    st.markdown('</div>', unsafe_allow_html=True)

# ---- TOP ISSUES ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🏆 Top Issues")

categories = [analyze(h) for h in st.session_state.history]
top = Counter(categories).most_common(3)

if top:
    for t in top:
        st.write(f"🔹 {t[0]} — {t[1]} reports")
else:
    st.write("No data yet")

st.markdown('</div>', unsafe_allow_html=True)

# ---- HEATMAP ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📊 Issue Zones")

data = pd.DataFrame({
    "Area": ["Hostel", "Library", "Block A"],
    "Count": [
        sum("hostel" in h.lower() for h in st.session_state.history),
        sum("library" in h.lower() for h in st.session_state.history),
        sum("block" in h.lower() for h in st.session_state.history),
    ]
})

st.bar_chart(data.set_index("Area"))
st.markdown('</div>', unsafe_allow_html=True)

# ---- LIVE FEED ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🌊 Live Campus Feed")

if st.session_state.history:
    for h in st.session_state.history[::-1]:
        st.write(f"⚡ {h}")
else:
    st.write("No activity yet")

st.markdown('</div>', unsafe_allow_html=True)

# ---- FUTURE PREDICTION ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔮 Future Prediction")

alerts = predict(st.session_state.history)
for a in alerts:
    st.info(a)

st.markdown('</div>', unsafe_allow_html=True)

# ---- OFFLINE MODE ----
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🔌 Offline Mode")
st.write("✔ Stores issues locally if no internet")
st.caption("Future upgrade: sync when connection is restored")

st.markdown('</div>', unsafe_allow_html=True)

st.caption("🏆 Built for Hackathon — Student Survival AI")
