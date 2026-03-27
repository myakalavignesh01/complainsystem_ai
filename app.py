import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import datetime
from sklearn.linear_model import LinearRegression

# ===============================
# 🔐 PASTE YOUR API KEY HERE
# ===============================
OPENAI_API_KEY = "sk-...GQUA"

# ===============================
# 🤖 AI FUNCTION (SAFE + FALLBACK)
# ===============================
def ai_solve(problem):
    try:
        if OPENAI_API_KEY == "sk-...GQUA":
            raise Exception("No API Key")

        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a network engineer AI. Give clear solutions."},
                {"role": "user", "content": problem}
            ]
        )
        return response.choices[0].message.content

    except:
        # 🔥 Fallback AI (important for demo)
        if "slow" in problem.lower():
            return "⚡ Network congestion detected. Reduce users or upgrade bandwidth."
        elif "no signal" in problem.lower():
            return "📡 Dead zone. Add router or repeater."
        elif "disconnect" in problem.lower():
            return "🔁 Signal instability. Check router placement."
        else:
            return "🛠 General issue. Optimize router placement and reduce interference."

# ===============================
# 🎨 UI
# ===============================
st.set_page_config(page_title="AI WiFi Solver", layout="wide")

st.title("🚀 AI WiFi Problem Solver (Final System)")
st.caption("Real AI + Backup AI • Heatmap • Smart Complaints")

# ===============================
# 📊 HEATMAP DATA
# ===============================
grid = st.sidebar.slider("Grid Size", 6, 20, 10)

np.random.seed(42)
signal = np.random.randint(-90, -30, (grid, grid))
df = pd.DataFrame(signal)

st.subheader("📡 WiFi Heatmap")
fig = px.imshow(df, color_continuous_scale='RdYlGn')
st.plotly_chart(fig, use_container_width=True)

# ===============================
# 📉 WEAK ZONES
# ===============================
threshold = -70
weak = np.where(signal < threshold)
weak_count = len(weak[0])

col1, col2, col3 = st.columns(3)
col1.metric("Weak Zones", weak_count)
col2.metric("Avg Signal", int(np.mean(signal)))
col3.metric("Max Signal", int(np.max(signal)))

# ===============================
# 🧠 PREDICTION
# ===============================
st.subheader("🧠 Prediction")

X = np.arange(len(signal.flatten())).reshape(-1,1)
y = signal.flatten()

model = LinearRegression()
model.fit(X, y)

future = np.arange(len(X), len(X)+20).reshape(-1,1)
pred = model.predict(future)

st.line_chart(pred)

# ===============================
# 🤖 AI SOLVER
# ===============================
st.subheader("🤖 AI Problem Solver")

problem = st.text_area("Enter any WiFi problem")

if st.button("Solve"):
    if problem:
        with st.spinner("AI thinking..."):
            solution = ai_solve(problem)
            st.success("Solution:")
            st.write(solution)
    else:
        st.warning("Enter problem first")

# ===============================
# 📩 COMPLAINT SYSTEM
# ===============================
st.subheader("📩 Complaint System")

if "data" not in st.session_state:
    st.session_state.data = []

location = st.text_input("Location")
issue = st.text_input("Issue")

if st.button("Submit Complaint"):
    solution = ai_solve(issue)

    entry = {
        "Location": location,
        "Issue": issue,
        "Solution": solution,
        "Time": datetime.now().strftime("%H:%M:%S")
    }

    st.session_state.data.append(entry)

    st.success("Complaint submitted + solved")

# ===============================
# 📊 DASHBOARD
# ===============================
st.subheader("📊 Dashboard")

if st.session_state.data:
    df2 = pd.DataFrame(st.session_state.data)
    st.dataframe(df2)

    chart = px.histogram(df2, x="Location")
    st.plotly_chart(chart, use_container_width=True)

else:
    st.info("No data yet")

# ===============================
# 🏁 FOOTER
# ===============================
st.markdown("---")
st.caption("🏆 Hackathon Ready AI System")
