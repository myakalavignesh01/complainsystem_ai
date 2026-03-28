import streamlit as st
import pandas as pd
import datetime, json, uuid, time, random, os
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import numpy as np

# VISUAL + MAP
import folium
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

# AI + EMAIL
from openai import OpenAI
import smtplib
from email.mime.text import MIMEText

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ResolveAI BAAP LEVEL", layout="wide")

# ---------------- API KEYS (SAFE) ----------------
client = OpenAI(api_key=os.getenv("sk-...k2IA"))

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# ---------------- LOGIN ----------------
USERS = {
    "admin": {"pwd": "1234", "role": "admin"},
    "student": {"pwd": "1111", "role": "user"}
}

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None

def login():
    st.title("🔐 ResolveAI Secure Login")
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

st.title("🚀 ResolveAI BAAP LEVEL AI SYSTEM")

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

def sentiment_priority(text):
    s = TextBlob(text).sentiment.polarity
    if s < -0.5: return "High"
    elif s < 0: return "Medium"
    return "Low"

def smart_score(text):
    score = 50
    if "urgent" in text.lower(): score += 20
    if "not working" in text.lower(): score += 20
    score += abs(TextBlob(text).sentiment.polarity) * 30
    return min(int(score), 100)

def detect_duplicate(text):
    texts = [h["text"] for h in st.session_state.history]
    texts.append(text)
    if len(texts) < 2: return False
    tfidf = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(tfidf[-1], tfidf[:-1])
    return sim.max() > 0.7

# ---------------- GPT AI ----------------
def gpt_ai_analysis(text):
    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a campus AI problem predictor."},
                {"role":"user","content":text}
            ]
        )
        return res.choices[0].message.content
    except:
        return "AI unavailable"

# ---------------- EMAIL ----------------
def send_email_alert(subject, message):
    try:
        msg = MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_USER

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
    except:
        pass

# ---------------- HEATMAP ----------------
def wifi_heatmap(data):
    m = folium.Map(location=[17.38,78.48], zoom_start=15)
    for d in data:
        if d["issue"] == "Network":
            color = "green"
            if d["priority"] == "High": color = "red"
            elif d["priority"] == "Medium": color = "orange"

            folium.CircleMarker(
                location=[d["lat"], d["lon"]],
                radius=10,
                color=color,
                fill=True
            ).add_to(m)
    st_folium(m, width=900)

# ---------------- PREDICTION ----------------
def predict_wifi_failure(data):
    loc_count = defaultdict(int)
    for d in data:
        if d["issue"] == "Network":
            loc_count[d["location"]] += 1

    alerts = []
    for loc, count in loc_count.items():
        if count >= 5:
            alerts.append(f"🚨 WiFi Failure Likely at {loc}")
    return alerts

# ---------------- ADVANCED AI ----------------
def anomaly_detection(data):
    scores = [d.get("score",50) for d in data]
    if len(scores) < 5: return []
    mean, std = np.mean(scores), np.std(scores)
    return [f"🚨 Anomaly at {d['location']}"
            for d in data if d.get("score",50) > mean + 2*std]

def complaint_clusters(data):
    texts = [d["text"] for d in data]
    if len(texts) < 2: return []
    vec = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(vec)
    clusters = []
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            if sim[i][j] > 0.8:
                clusters.append("🔁 Similar complaints detected")
    return clusters

def campus_health_score(data):
    if not data: return 100
    avg = sum([d.get("score",50) for d in data]) / len(data)
    return int(100 - avg)

# ---------------- IoT SIMULATION ----------------
def wifi_signal_chart():
    locations = ["Hostel A","Hostel B","Library","Canteen"]
    signals = [random.randint(20,100) for _ in locations]

    fig, ax = plt.subplots()
    ax.bar(locations, signals)
    st.pyplot(fig)

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["🧑 User","🛠 Admin","📊 Analytics"])

# ---------------- USER ----------------
with tab1:
    st.subheader("Submit Complaint")

    user = st.text_input("User ID")
    location = st.text_input("Location")
    lat = st.number_input("Latitude", value=17.38)
    lon = st.number_input("Longitude", value=78.48)
    text = st.text_area("Complaint")

    if st.button("Submit Complaint"):
        if text:
            issue = detect_issue(text)

            entry = {
                "ticket": str(uuid.uuid4())[:8],
                "user": user,
                "text": text,
                "issue": issue,
                "location": location,
                "lat": lat,
                "lon": lon,
                "priority": sentiment_priority(text),
                "score": smart_score(text),
                "time": str(datetime.datetime.now())
            }

            st.session_state.history.append(entry)
            save()

            st.success("Complaint Submitted!")

            # GPT AI
            ai = gpt_ai_analysis(text)
            st.info(f"🤖 AI Insight: {ai}")

            # Email alert
            if entry["priority"] == "High":
                send_email_alert("🚨 High Priority Issue", text)

            if detect_duplicate(text):
                st.warning("Duplicate complaint detected!")

# ---------------- ADMIN ----------------
with tab2:
    st.subheader("Admin Panel")
    for h in st.session_state.history:
        st.write(h)

# ---------------- ANALYTICS ----------------
with tab3:
    st.subheader("Dashboard")
    df = pd.DataFrame(st.session_state.history)

    if not df.empty:
        st.metric("Total Complaints", len(df))
        st.bar_chart(df["issue"].value_counts())

        st.subheader("📶 WiFi Heatmap")
        wifi_heatmap(st.session_state.history)

        st.subheader("🤖 Predictions")
        for p in predict_wifi_failure(st.session_state.history):
            st.error(p)

        st.subheader("🚨 Anomalies")
        for a in anomaly_detection(st.session_state.history):
            st.warning(a)

        st.subheader("🧠 Complaint Clusters")
        for c in complaint_clusters(st.session_state.history):
            st.info(c)

        st.subheader("🏫 Campus Health Score")
        score = campus_health_score(st.session_state.history)
        st.metric("Health Score", score)

        st.subheader("📡 Live WiFi Signal")
        wifi_signal_chart()

        st.subheader("🔮 What-if Simulation")
        test = st.slider("Simulate complaints",1,10,5)
        if test > 7:
            st.error("🚨 Failure likely")
        else:
            st.warning("⚠️ Moderate risk")

# ---------------- RESET ----------------
if st.button("Clear Data"):
    st.session_state.history = []
    save()
