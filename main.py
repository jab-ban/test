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
            return response.json()
        except:
            return {"error": "Invalid JSON", "raw": response.text}


# ---------- Streamlit Config ----------
st.set_page_config(page_title="💬 Communication Hub", page_icon="💎", layout="centered")


# ---------- NEW FIXED BEAUTIFUL UI (NO TRANSPARENCY) ----------
st.markdown("""
<style>

    /* Background */
    html, body {
        background:
            linear-gradient(135deg, rgba(100,150,255,0.75), rgba(180,120,255,0.75)),
            url('https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?auto=format&fit=crop&w=1920&q=80');
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        font-family: 'Poppins', sans-serif;
    }

    /* Main Card */
    section.main > div {
        background: #ffffffee !important;
        border-radius: 22px !important;
        padding: 3rem !important;
        border: 1px solid #e2e2e2 !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.18) !important;
        animation: fadeIn .7s ease;
    }

    @keyframes fadeIn {
        from {opacity:0; transform: translateY(10px);}
        to   {opacity:1; transform: translateY(0);}
    }

    /* Titles */
    h1 {
        text-align: center !important;
        color:#1e3a8a !important;
        font-size: 2.6rem !important;
        font-weight: 900 !important;
    }

    h3 {
        text-align:center !important;
        color:#475569 !important;
        font-weight: 500 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #2563eb, #a855f7) !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 0.9rem 2rem !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        width: 100% !important;
        transition: .25s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(59,130,246,0.4);
    }

    /* Inputs */
    .stTextInput input, textarea {
        background: #ffffff !important;
        border: 1px solid #d1d1d1 !important;
        border-radius: 12px !important;
        padding: .8rem !important;
    }

    .stSelectbox div[data-baseweb="select"] > div {
        background: #ffffff !important;
        border: 1px solid #d1d1d1 !important;
        border-radius: 12px !important;
    }

</style>
""", unsafe_allow_html=True)



# ---------- Layout ----------
st.title("💬 Communication Hub")
st.write("### Send your messages professionally via Email or WhatsApp 🚀")


# ---------- Load CSV ----------
try:
    receivers_df = pd.read_csv(io.StringIO(st.secrets["MAILS_CSV"]))
    senders_df = pd.read_csv(io.StringIO(st.secrets["SENDERS_CSV"]))
    st.success(f"✔ Loaded {len(receivers_df)} receivers | {len(senders_df)} senders")
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()


# ---------- User Input ----------
method = st.selectbox("Choose Send Method", ["Email", "WhatsApp"])

if method == "Email":
    subject = st.text_input("Email Subject", "Test Email")
    body_template = st.text_area("Email Body", "Hello {name},\nThis is a test email!")
else:
    body_template = st.text_area("WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")


# ---------- Filter by Department ----------
if "dept" in receivers_df.columns:
    depts = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected = st.multiselect("Choose Department(s)", depts, default=depts)
    filtered_df = receivers_df if not selected else receivers_df[receivers_df["dept"].isin(selected)]
else:
    filtered_df = receivers_df


# ---------- SEND BUTTON ----------
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages"):
    st.success("✨ Sending started...")

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
                api.send_message(row["number"], message)

            sent_count += 1

        except Exception as e:
            st.error(f"❌ Failed for {name}: {e}")

        time.sleep(1.5)

    st.success(f"🎉 Done! Sent {sent_count}/{total} successfully!")

