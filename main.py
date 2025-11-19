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

# ---------- Load environment variables ----------
load_dotenv()

# ---------- Secure Secrets Loader ----------
def get_secret(key: str):
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key)

# ---------- Evolution API Class ----------
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
            res_json = response.json()
        except Exception:
            res_json = {"error": "Invalid JSON response", "raw": response.text}
        print("📩 API Response:", res_json)
        return res_json


# ---------- Streamlit Page Config ----------
st.set_page_config(page_title="💬 Communication Hub", page_icon="💎", layout="centered")

# ---------- FIXED + WORKING GLASS PREMIUM CSS ----------
st.markdown("""
<style>

    /* ----- Global Background ----- */
    html, body {
        background: linear-gradient(135deg, #eef2ff 0%, #dbe4ff 50%, #e0e7ff 100%) !important;
        font-family: 'Poppins', sans-serif;
    }

    /* ----- Main Streamlit Container ----- */
    section.main > div { 
        background: rgba(255,255,255,0.25) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 25px !important;
        padding: 3rem !important;
        border: 1px solid rgba(255,255,255,0.45) !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.08) !important;
        animation: fadeIn 0.9s ease !important;
    }

    /* Fade In */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(15px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Titles */
    h1 {
        text-align: center !important;
        font-weight: 800 !important;
        color: #1e3a8a !important;
        letter-spacing: -1px !important;
    }
    h3 {
        text-align:center !important;
        color:#475569 !important;
        font-weight: 400 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: .9rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        box-shadow: 0 10px 25px rgba(37,99,235,.35) !important;
        transition: .3s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg,#1e40af,#2563eb) !important;
        transform: translateY(-3px) !important;
        box-shadow: 0 14px 30px rgba(37,99,235,.45) !important;
    }

    /* Inputs */
    .stTextInput>div>div>input, textarea {
        border-radius: 12px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: #f8fafc !important;
        padding: .7rem !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 12px !important;
        background-color: #f1f5f9 !important;
        border: 1px solid #cbd5e1 !important;
    }

</style>
""", unsafe_allow_html=True)


# ---------- Title ----------
st.title("💬 Communication Hub")
st.write("### Send your messages professionally via Email or WhatsApp 🚀")


# ---------- Load CSV Files ----------
try:
    receivers_df = pd.read_csv(io.StringIO(st.secrets["MAILS_CSV"]))
    senders_df = pd.read_csv(io.StringIO(st.secrets["SENDERS_CSV"]))
    st.success(f"✔ Loaded: {len(receivers_df)} receivers | {len(senders_df)} senders")
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# ---------- User Selections ----------
method = st.selectbox("Send Method", ["Email", "WhatsApp"])
delay = 2

if method == "Email":
    subject = st.text_input("Email Subject", "Test Email")
    body_template = st.text_area("Email Body", "Hello {name},\nThis is a test email.")
else:
    subject = None
    body_template = st.text_area("WhatsApp Message", "Hi {name}, this is a WhatsApp test message!")

# ---------- Department Filter ----------
if "dept" in receivers_df.columns:
    departments = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected = st.multiselect("Choose Department(s)", options=departments, default=departments)
    filtered_df = receivers_df if not selected else receivers_df[receivers_df["dept"].isin(selected)]
else:
    st.error("❌ 'dept' column missing!")
    filtered_df = receivers_df

# ---------- WhatsApp Check ----------
if method == "WhatsApp" and "number" not in filtered_df.columns:
    st.error("❌ Missing 'number' column!")
    st.stop()

# ---------- Send Section ----------
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages"):
    st.success("Sending started... ⚡")

    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))
    api = EvolutionAPI()

    for _, row in filtered_df.iterrows():
        name = row["name"]
        message = body_template.format(name=name)

        try:
            if method == "Email":
                sender = next(senders_cycle)
                sender_email = sender["email"]
                password = sender["app_password"]
                receiver = row["email"]

                msg = MIMEText(message)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = receiver

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
                server.quit()

            else:
                api.send_message(str(row["number"]), message)

            sent_count += 1

        except Exception as e:
            st.error(f"❌ Error sending to {name}: {e}")

        time.sleep(delay)

    st.success(f"🎉 Done! Successfully sent {sent_count}/{total} messages.")
