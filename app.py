import streamlit as st
import pandas as pd
import datetime, json, uuid, random, os
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ResolveAI FINAL", layout="wide")

# ---------------- SAFE AI SETUP ----------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def ai_insight(text):
    if not OPENAI_API_KEY:
        return "⚠️ AI not configured"

    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Analyze campus complaint: give issue, cause, prediction, solution."},
                {"role": "user", "content": text}
            ]
        )

        return res.choices[0].message.content

    except:
        return "⚠️ AI unavailable"

# ---------------- LOGIN ----------------
USERS = {
    "admin": {"pwd": "1234", "role": "admin"},
    "student": {"pwd": "1111", "role": "user"}
}

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

def login():
    st.title("🔐 ResolveAI Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in USERS and USERS[u]["pwd"] == p:
            st.session_state.login = True
            st.session_state.role = USERS[u]["role"]
            st.rerun()
        else:
            st.error("Invalid Credentials")

if not st.session_state.login:
    login()
    st.stop()

# ---------------- UI ----------------
st.markdown("""
<style>
body {background:#020617;color:white;}
h1,h2,h3{color:#00ffff;}
.stButton>button {
background: linear-gradient(90deg,#00ffff,#0077ff);
color:black;border-radius:10px;}
</style>
""", unsafe_allow_html=True)

st.title("🚀 ResolveAI AI Prediction System")

# ---------------- DATA ----------------
if "history" not in st.session_state:
    st.session_state.history = []

def save():
    with open("data.json", "w") as f:
        json.dump(st.session_state.history, f)

def load():
    try:
        with open("data.json") as f:
            st.session_state.history = json.load(f)
    except:
        st.session_state.history = []

load()

# ---------------- CORE AI ----------------
def detect_issue(text):
    t = text.lower()
    if "wifi" in t: return "Network"
    elif "food" in t: return "Food"
    elif "water" in t: return "Water"
    elif "power" in t: return "Electric"
    return "General"

def priority(text):
    s = TextBlob(text).sentiment.polarity
    if s < -0.5: return "High"
    elif s < 0: return "Medium"
    return "Low"

def score(text):
    sc = 50
    if "urgent" in text.lower(): sc += 20
    if "not working" in text.lower(): sc += 20
    sc += abs(TextBlob(text).sentiment.polarity) * 30
    return min(100, int(sc))

def duplicate(text):
    texts = [h["text"] for h in st.session_state.history]
    texts.append(text)
    if len(texts) < 2: return False
    tfidf = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(tfidf[-1], tfidf[:-1])
    return sim.max() > 0.7

# ---------------- PREDICTION ----------------
def predict(data):
    locs = defaultdict(int)
    for d in data:
        if d["issue"] == "Network":
            locs[d["location"]] += 1

    alerts = []
    for loc, count in locs.items():
        if count >= 5:
            alerts.append(f"🚨 WiFi failure likely at {loc}")
    return alerts

# ---------------- ANALYTICS ----------------
def anomaly(data):
    scores = [d.get("score",50) for d in data]
    if len(scores) < 5: return []
    m, s = np.mean(scores), np.std(scores)

    return [f"🚨 Anomaly at {d['location']}"
            for d in data if d.get("score",50) > m + 2*s]

def clusters(data):
    texts = [d["text"] for d in data]
    if len(texts) < 2: return []
    vec = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(vec)

    res = []
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            if sim[i][j] > 0.8:
                res.append("🔁 Similar complaints detected")
    return res

def health(data):
    if not data: return 100
    avg = sum([d.get("score",50) for d in data]) / len(data)
    return int(100 - avg)

# ---------------- SAFE HEATMAP ----------------
def safe_wifi_heatmap(data):
    loc_counts = {}

    for d in data:
        if isinstance(d, dict) and d.get("issue") == "Network":
            loc = d.get("location", "Unknown")
            loc_counts[loc] = loc_counts.get(loc, 0) + 1

    if not loc_counts:
        st.info("No WiFi complaints yet")
        return

    df = pd.DataFrame(list(loc_counts.items()), columns=["Location", "Count"])
    df = df.sort_values(by="Count", ascending=False)

    st.dataframe(df, use_container_width=True)

    fig, ax = plt.subplots()
    ax.barh(df["Location"], df["Count"])
    ax.invert_yaxis()

    st.pyplot(fig)

# ---------------- SIMULATION ----------------
def wifi_signal_chart():
    locations = ["Hostel A","Hostel B","Library","Canteen"]
    signals = [random.randint(20,100) for _ in locations]

    fig, ax = plt.subplots()
    ax.bar(locations, signals)
    st.pyplot(fig)

# ---------------- TABS ----------------
t1, t2, t3 = st.tabs(["User","Admin","Analytics"])

# ---------------- USER ----------------
with t1:
    st.subheader("Submit Complaint")

    user = st.text_input("User ID")
    loc = st.text_input("Location")
    text = st.text_area("Complaint")

    if st.button("Submit Complaint"):
        if text:
            entry = {
                "ticket": str(uuid.uuid4())[:6],
                "user": user,
                "text": text,
                "issue": detect_issue(text),
                "location": loc,
                "priority": priority(text),
                "score": score(text),
                "time": str(datetime.datetime.now())
            }

            st.session_state.history.append(entry)
            save()

            st.success("Complaint Submitted!")

            # 🤖 AI Insight
            ai_output = ai_insight(text)
            st.info(f"🤖 AI Insight:\n{ai_output}")

            if duplicate(text):
                st.warning("Duplicate complaint detected!")

# ---------------- ADMIN ----------------
with t2:
    st.subheader("Admin Panel")
    for h in st.session_state.history:
        st.write(h)

# ---------------- ANALYTICS ----------------
with t3:
    st.subheader("Dashboard")
    df = pd.DataFrame(st.session_state.history)

    if not df.empty:
        st.metric("Total Complaints", len(df))
        st.bar_chart(df["issue"].value_counts())

        st.subheader("📶 WiFi Heatmap")
        safe_wifi_heatmap(st.session_state.history)

        st.subheader("🤖 Predictions")
        for p in predict(st.session_state.history):
            st.error(p)

        st.subheader("🚨 Anomalies")
        for a in anomaly(st.session_state.history):
            st.warning(a)

        st.subheader("🧠 Complaint Clusters")
        for c in clusters(st.session_state.history):
            st.info(c)

        st.subheader("🏫 Campus Health Score")
        st.metric("Score", health(st.session_state.history))

        st.subheader("📡 WiFi Simulation")
        wifi_signal_chart()

        st.subheader("🧠 AI Summary")
        all_text = " ".join([d.get("text","") for d in st.session_state.history])
        st.info(ai_insight(all_text))

# ---------------- RESET ----------------
if st.button("Reset Data"):
    st.session_state.history = []
    save()
