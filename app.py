import streamlit as st
import random
import textwrap
import pandas as pd
from datetime import datetime
import csv
import os

st.set_page_config(
    page_title="Phishing Trainer SA",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for nicer look
st.markdown("""
    <style>
    .stButton>button { width: 100%; }
    .stRadio>label { font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# ====================== LOAD DATA ======================
@st.cache_data
def load_data():
    phishing = []
    legit = []
    files = ["data/CEAS_08.csv", "data/Enron.csv"]
    for file in files:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file, encoding='latin1', on_bad_lines='skip')
                phishing_mask = df['label'].astype(str).str.contains('1|phishing|spam', case=False, na=False)
                phishing.extend(df[phishing_mask][['subject', 'body']].to_dict('records'))
                legit.extend(df[~phishing_mask][['subject', 'body']].to_dict('records'))
            except:
                pass
    return phishing, legit

phishing_examples, legit_examples = load_data()

# ====================== SESSION STATE ======================
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False
if "current_question" not in st.session_state:
    st.session_state.current_question = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 8
if "current_subject" not in st.session_state:
    st.session_state.current_subject = ""
if "current_body" not in st.session_state:
    st.session_state.current_body = ""
if "current_is_phishing" not in st.session_state:
    st.session_state.current_is_phishing = False

# ====================== HELPERS ======================
def generate_example(is_phishing):
    if is_phishing and phishing_examples:
        ex = random.choice(phishing_examples)
    elif legit_examples:
        ex = random.choice(legit_examples)
    else:
        ex = {"subject": "Test", "body": "Fallback"}
    return ex["subject"], ex.get("body", "")[:550]

def get_red_flags(subject, body):
    text = (subject + " " + body).lower()
    flags = []
    if any(w in text for w in ["urgent", "immediately", "suspended", "locked", "verify now"]):
        flags.append("🚨 Urgent / threatening language")
    if any(w in text for w in ["click here", "update your", "confirm", "login"]):
        flags.append("🔗 Suspicious call-to-action")
    if any(w in text for w in ["password", "bank details", "card"]):
        flags.append("💰 Asking for sensitive information")
    if "winner" in text or "prize" in text or "refund" in text:
        flags.append("🎁 Too-good-to-be-true")
    return flags or ["No obvious red flags"]

def save_score(score, total):
    try:
        with open('score_history.csv', 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), score, total])
    except:
        pass

# ====================== SIDEBAR ======================
st.sidebar.title("🛡️ Phishing Trainer")
page = st.sidebar.radio("Go to", ["🏠 Home", "🎯 Take the Quiz", "📊 My Scores", "ℹ️ About"])

# ====================== HOME ======================
if page == "🏠 Home":
    st.title("🛡️ Phishing Awareness Trainer")
    st.markdown("Train with **real** phishing emails from a 70k+ Kaggle dataset.")
    st.info("Go to **Take the Quiz** in the sidebar to begin.")

# ====================== QUIZ ======================
elif page == "🎯 Take the Quiz":
    st.title("🎯 Phishing Awareness Quiz")

    if not st.session_state.quiz_started:
        st.session_state.num_questions = st.slider("Number of questions", 5, 15, 8)
        if st.button("🚀 Start New Quiz", type="primary"):
            st.session_state.quiz_started = True
            st.session_state.current_question = 0
            st.session_state.score = 0
            # Generate FIRST question immediately
            is_phish = random.choice([True, False])
            st.session_state.current_subject, st.session_state.current_body = generate_example(is_phish)
            st.session_state.current_is_phishing = is_phish
            st.rerun()

    else:
        q = st.session_state.current_question + 1
        total = st.session_state.num_questions

        st.progress(q / total)
        st.caption(f"Question {q} of {total}")

        # Display the LOCKED question
        st.subheader(f"Question {q}")
        st.write(f"**Subject:** {st.session_state.current_subject}")
        st.write("**Body:**")
        st.write(textwrap.fill(st.session_state.current_body, width=80))

        # Answer radio — this will NOT change the question anymore
        user_answer = st.radio(
            "Is this email **phishing**?",
            ["Yes", "No"],
            key=f"radio_{st.session_state.current_question}"  # unique key
        )

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✅ Submit Answer", type="primary"):
                correct = (user_answer == "Yes" and st.session_state.current_is_phishing) or \
                          (user_answer == "No" and not st.session_state.current_is_phishing)

                if correct:
                    st.session_state.score += 1
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Wrong!")

                # Show explanation
                st.caption("**Explanation & Red Flags:**")
                for flag in get_red_flags(st.session_state.current_subject, st.session_state.current_body):
                    st.caption(f"• {flag}")

                # Move to next question
                st.session_state.current_question += 1

                if st.session_state.current_question >= st.session_state.num_questions:
                    # Quiz finished
                    percentage = int((st.session_state.score / st.session_state.num_questions) * 100)
                    save_score(st.session_state.score, st.session_state.num_questions)

                    st.success(f"🏆 Quiz Complete! Score: {st.session_state.score}/{st.session_state.num_questions} ({percentage}%)")
                    if percentage >= 90:
                        st.balloons()
                        st.success("🌟 Phishing expert level!")
                    elif percentage >= 70:
                        st.warning("👍 Good job!")
                    else:
                        st.info("💡 More practice will help!")

                    if st.button("Start New Quiz"):
                        st.session_state.quiz_started = False
                        st.rerun()
                else:
                    # Generate NEXT question and store it
                    is_phish = random.choice([True, False])
                    st.session_state.current_subject, st.session_state.current_body = generate_example(is_phish)
                    st.session_state.current_is_phishing = is_phish
                    st.rerun()

        with col2:
            if st.button("Restart Quiz"):
                st.session_state.quiz_started = False
                st.rerun()

# ====================== SCORES & ABOUT (unchanged) ======================
elif page == "📊 My Scores":
    st.title("📊 Your Training History")
    if os.path.exists("score_history.csv"):
        df = pd.read_csv("score_history.csv", names=["Date", "Score", "Total"])
        st.dataframe(df.sort_values("Date", ascending=False))
        st.line_chart(df.set_index("Date")["Score"])
    else:
        st.info("Take a quiz first!")

elif page == "ℹ️ About":
    st.title("About")
    st.markdown("Built by Tumiso in Mbombela using real Kaggle phishing emails + Streamlit.")

st.sidebar.caption("Made in Mpumalanga • February 2026")