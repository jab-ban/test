import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
import requests
import os
from dotenv import load_dotenv
import io

load_dotenv()

def get_secret(key: str):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)


class EvolutionAPI:
    def __init__(self):
        self.BASE_URL = get_secret("EVO_BASE_URL")
        self.INSTANCE_NAME = get_secret("EVO_INSTANCE_NAME")
        self.__api_key = get_secret("AUTHENTICATION_API_KEY")

        self.__headers = {
            'apikey': self.__api_key,
            'Content-Type': 'application/json'
        }

    def send_message(self, number, text):
        payload = {'number': str(number).strip(), 'text': text}
        response = requests.post(
            url=f'{self.BASE_URL}/message/sendText/{self.INSTANCE_NAME}',
            headers=self.__headers,
            json=payload
        )
        try:
            return response.json()
        except:
            return {"error": "Invalid JSON", "raw": response.text}



# ------------------ STREAMLIT PAGE CONFIG ------------------
st.set_page_config(page_title="💬 Communication Hub", page_icon="💎", layout="centered")

# ------------------ ADVANCED PREMIUM UI ------------------
st.markdown("""
<style>

    /* -------- BACKGROUND -------- */
    html, body {
        background: 
            linear-gradient(135deg, rgba(140,180,255,0.45), rgba(180,140,255,0.45)),
            url('https://images.unsplash.com/photo-1522199710521-72d69614c702?auto=format&fit=crop&w=1920&q=80');
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Poppins', sans-serif;
        animation: fadeBg 18s ease-in-out infinite alternate;
    }

    @keyframes fadeBg {
        0% { filter: brightness(0.95) saturate(1.1); }
        100% { filter: brightness(1.1) saturate(1.3); }
    }

    /* -------- MAIN CENTERED CARD -------- */
    section.main > div {
        background: rgba(255,255,255,0.20) !important;
        backdrop-filter: blur(22px) !important;
        border-radius: 28px !important;
        padding: 3rem !important;
        border: 1px solid rgba(255,255,255,0.45) !important;
        box-shadow: 0 20px 70px rgba(0,0,0,0.20) !important;
        animation: slideDown 0.8s ease !important;
    }

    @keyframes slideDown {
        from { opacity:0; transform: translateY(-20px); }
        to   { opacity:1; transform: translateY(0); }
    }

    /* -------- HEADERS -------- */
    h1 {
        text-align: center !important;
        font-weight: 900 !important;
        font-size: 2.8rem !important;
        background: linear-gradient(90deg, #3b82f6, #a855f7);
        -webkit-background-clip: text;
        color: transparent;
        animation: glow 2.5s ease-in-out infinite alternate;
    }

    @keyframes glow {
        0% { text-shadow: 0 0 18px rgba(59,130,246,0.4); }
        100% { text-shadow: 0 0 28px rgba(168,85,247,0.5); }
    }

    h3 {
        text-align:center !important;
        color:#334155 !important;
        font-weight: 500 !important;
        opacity: .85 !important;
    }

    /* -------- BUTTONS -------- */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #a855f7) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 12px 35px rgba(59,130,246,.45) !important;
        transition: 0.3s ease !important;
        animation: pulseBtn 2.5s infinite ease-in-out alternate;
    }

    @keyframes pulseBtn {
        0% { transform: scale(1); box-shadow: 0 10px 25px rgba(59,130,246,0.34); }
        100% { transform: scale(1.03); box-shadow: 0 15px 45px rgba(168,85,247,0.45); }
    }

    .stButton > button:hover {
        transform: translateY(-4px) scale(1.03) !important;
        box-shadow: 0 18px 55px rgba(59,130,246,.55) !important;
    }

    /* -------- INPUTS -------- */
    .stTextInput input, textarea {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.65) !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
        padding: .8rem !important;
        transition: .25s;
    }
    .stTextInput input:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 12px rgba(124,58,237,0.5) !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 14px !important;
        background: rgba(255,255,255,0.65) !important;
        border: 1px solid rgba(255,255,255,0.35) !important;
    }

</style>
""", unsafe_allow_html=True)


# ------------------ PAGE CONTENT ------------------
st.title("💬 Communication Hub")
st.write("### Send your messages in a professional & beautiful interface 🚀")


# ------------------ LOAD CSV ------------------
try:
    receivers_df = pd.read_csv(io.StringIO(st.secrets["MAILS_CSV"]))
    senders_df = pd.read_csv(io.StringIO(st.secrets["SENDERS_CSV"]))
    st.success(f"Loaded {len(receivers_df)} receivers & {len(senders_df)} senders ✔")
except Exception as e:
    st.error(f"CSV Error: {e}")
    st.stop()


# ------------------ USER INPUTS ------------------
method = st.selectbox("Choose Sending Method", ["Email", "WhatsApp"])

if method == "Email":
    subject = st.text_input("Email Subject", "Test Email")
    body_template = st.text_area("Email Body", "Hello {name},\nThis is a test email.")
else:
    body_template = st.text_area("WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")


# ------------------ FILTER BY DEPARTMENT ------------------
if "dept" in receivers_df.columns:
    depts = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected = st.multiselect("Choose Departments", options=depts, default=depts)
    filtered_df = receivers_df if not selected else receivers_df[receivers_df["dept"].isin(selected)]
else:
    filtered_df = receivers_df


# ------------------ SEND LOGIC ------------------
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages"):
    st.success("Sending messages... ⚡")

    total = len(filtered_df)
    sent_count = 0
    api = EvolutionAPI()
    sender_cycle = cycle(senders_df.to_dict(orient="records"))

    for _, row in filtered_df.iterrows():

        name = row["name"]
        message = body_template.format(name=name)

        try:
            if method == "Email":
                sender = next(sender_cycle)
                sender_email = sender["email"]
                app_pw = sender["app_password"]

                msg = MIMEText(message)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = row["email"]

                s = smtplib.SMTP("smtp.gmail.com", 587)
                s.starttls()
                s.login(sender_email, app_pw)
                s.send_message(msg)
                s.quit()

            else:
                api.send_message(str(row["number"]), message)

            sent_count += 1

        except Exception as e:
            st.error(f"Failed for {name}: {e}")

        time.sleep(1.8)

    st.success(f"🎉 Successfully sent {sent_count}/{total} messages!")


