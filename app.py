import streamlit as st
import pandas as pd
import datetime, json, uuid
import pdfplumber
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="ResolveAI System", layout="wide")

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
            st.success("Login Success")
            st.rerun()
        else:
            st.error("Invalid Credentials")

if not st.session_state.login:
    login()
    st.stop()

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {background:#020617;color:white;}
.card {
    background:#0f172a;
    padding:20px;
    border-radius:15px;
    margin:10px;
    box-shadow:0 0 20px rgba(0,255,255,0.2);
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 ResolveAI - Smart Grievance System")

# ---------------- DATA ----------------
if "history" not in st.session_state:
    st.session_state.history = []

def save():
    with open("data.json","w") as f:
        json.dump(st.session_state.history,f)

def load():
    try:
        with open("data.json") as f:
            st.session_state.history = json.load(f)
    except:
        pass

load()

# ---------------- AI ----------------
def analyze(text):
    t = text.lower()
    if "wifi" in t: return "Network"
    elif "water" in t: return "Water"
    elif "power" in t: return "Electric"
    return "General"

def priority(text):
    s = TextBlob(text).sentiment.polarity
    if s < -0.5: return "High"
    elif s < 0: return "Medium"
    return "Low"

def advanced_score(text):
    score = 50
    t = text.lower()

    if "urgent" in t: score += 25
    if "not working" in t: score += 15
    if TextBlob(text).sentiment.polarity < -0.5: score += 20

    return min(score, 100)

def duplicate(text):
    if not st.session_state.history:
        return False

    texts = [h["text"] for h in st.session_state.history] + [text]

    tfidf = TfidfVectorizer().fit_transform(texts)
    sim = cosine_similarity(tfidf[-1], tfidf[:-1])

    return sim.max() > 0.7

# ---------------- SYSTEM ----------------
def department(issue):
    return {
        "Network":"IT Dept",
        "Water":"Maintenance",
        "Electric":"Electrical",
        "General":"Admin"
    }.get(issue)

def assign_officer():
    officers = ["A","B","C","D"]
    return officers[len(st.session_state.history) % len(officers)]

def delay(entry):
    t = datetime.datetime.strptime(entry["time"], "%Y-%m-%d %H:%M")
    return (datetime.datetime.now() - t).total_seconds() > 60

def workflow(entry):
    if entry["status"] == "Received":
        entry["status"] = "Assigned"
    elif entry["status"] == "Assigned":
        entry["status"] = "Processing"
    elif entry["status"] == "Processing":
        entry["status"] = "Verified"
    elif entry["status"] == "Verified":
        entry["status"] = "Closed"

def escalate(entry):
    if delay(entry) and entry["status"] != "Closed":
        entry["priority"] = "High"
        entry["status"] = "Escalated"
        entry["officer"] = "Senior Officer"

# ---------------- TABS ----------------
tab1, tab2, tab3 = st.tabs(["🧑 User", "🛠 Admin", "📊 Analytics"])

# ---------------- USER ----------------
with tab1:
    user = st.text_input("User ID")
    text = st.text_area("Enter Complaint")

    file = st.file_uploader("Upload PDF")
    if file:
        try:
            with pdfplumber.open(file) as pdf:
                text = ""
                for p in pdf.pages:
                    page_text = p.extract_text()
                    if page_text:
                        text += page_text
        except:
            st.error("Error reading PDF")

    if st.button("Submit Complaint"):
        if text:
            ticket = str(uuid.uuid4())[:8]
            issue = analyze(text)

            entry = {
                "ticket": ticket,
                "user": user,
                "text": text,
                "issue": issue,
                "department": department(issue),
                "officer": assign_officer(),
                "priority": priority(text),
                "score": advanced_score(text),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "Received",
                "log": ["Created"]
            }

            st.session_state.history.append(entry)
            save()

            st.success(f"Ticket Created: {ticket}")

            if duplicate(text):
                st.warning("Duplicate Complaint Detected")

# ---------------- ADMIN ----------------
with tab2:
    st.subheader("Admin Panel")

    for i, h in enumerate(st.session_state.history):
        workflow(h)
        escalate(h)

        st.write(f"🎫 {h['ticket']} | {h['status']} | {h['priority']} | {h['officer']}")

        if st.session_state.role == "admin":
            msg = st.text_input(f"Reply {h['ticket']}", key=f"msg_{i}")
            if st.button(f"Send {h['ticket']}", key=f"btn_{i}"):
                h["response"] = msg
                h["log"].append("Responded")
                save()
                st.success("Response Sent")

# ---------------- ANALYTICS ----------------
with tab3:
    df = pd.DataFrame(st.session_state.history)

    if not df.empty:
        st.subheader("📊 KPI")
        total = len(df)
        closed = sum(df["status"] == "Closed")

        st.metric("Total", total)
        st.metric("Closed", closed)

        st.subheader("Trend")
        st.line_chart(df["time"].value_counts())

        st.subheader("Priority")
        st.bar_chart(df["priority"].value_counts())

        st.subheader("Departments")
        st.bar_chart(df["department"].value_counts())

        st.download_button("Download CSV", df.to_csv(), "report.csv")

# ---------------- SEARCH ----------------
search = st.text_input("Search")

for h in st.session_state.history:
    if search.lower() in h["text"].lower():
        st.write(h)

# ---------------- RESET ----------------
if st.button("Clear All Data"):
    st.session_state.history = []
    save()

st.caption("🏆 Ultimate AI Hackathon Project")
