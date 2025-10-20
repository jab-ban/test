import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
import requests
import os
from dotenv import load_dotenv

# ---------- Load environment variables ----------
load_dotenv()

class EvolutionAPI:
    BASE_URL = os.getenv("EVO_BASE_URL")
    INSTANCE_NAME = os.getenv("EVO_INSTANCE_NAME")

    def __init__(self):
        self.__api_key = os.getenv("AUTHENTICATION_API_KEY")
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


# ---------- Streamlit Config ----------
st.set_page_config(page_title="💬 Communication Hub", page_icon="💎", layout="centered")

# ---------- Ultra Modern CSS ----------
st.markdown("""
    <style>
        /* General Background */
        body {
            background: linear-gradient(135deg, #f0f4ff 0%, #eaf1fb 50%, #dee9ff 100%);
            font-family: 'Poppins', sans-serif;
        }
        .block-container {
            max-width: 900px !important;
            margin: auto;
            padding-top: 2rem !important;
        }

        /* Glassmorphic Card */
        .main-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(15px);
            padding: 3rem;
            border-radius: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.4);
            transition: transform 0.3s ease;
        }
        .main-card:hover {
            transform: scale(1.01);
        }

        /* Headings */
        h1 {
            color: #1e3a8a;
            font-weight: 800;
            font-size: 2.6rem;
            text-align: center;
            letter-spacing: -1px;
        }
        h3, h2, h4 {
            color: #475569;
            text-align: center;
            font-weight: 400;
        }
        hr {
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #94a3b8, transparent);
            margin: 2rem 0;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(90deg, #2563eb, #3b82f6, #2563eb);
            color: white !important;
            border-radius: 14px;
            font-weight: 600;
            padding: 0.9rem 2rem;
            border: none;
            font-size: 1.05rem;
            box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background: linear-gradient(90deg, #1d4ed8, #2563eb, #1d4ed8);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        /* Inputs */
        .stTextInput>div>div>input, textarea {
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
            padding: 0.6rem !important;
            font-size: 0.95rem !important;
        }
        textarea {
            height: 120px !important;
        }

        /* Select boxes */
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 12px !important;
            border: 1px solid #cbd5e1 !important;
            background-color: #f8fafc !important;
        }

        /* Alerts */
        .stAlert {
            border-radius: 15px !important;
            padding: 1rem 1.2rem !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.05);
            font-weight: 500;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 2.5rem;
            color: #6b7280;
            font-size: 0.9rem;
        }
        .footer a {
            color: #2563eb;
            text-decoration: none;
            font-weight: 600;
        }

        /* Animation for header emoji */
        .pulse {
            display: inline-block;
            animation: pulse 1.8s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.2); opacity: 0.7; }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Layout ----------
st.markdown('<div class="main-card">', unsafe_allow_html=True)

st.markdown('<h1><span class="pulse">💬</span> Communication Hub</h1>', unsafe_allow_html=True)
st.markdown("<h3>Send your messages professionally via Email or WhatsApp 🚀</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---------- CSV Load ----------
try:
    receivers_df = pd.read_csv('C:/Users/Ban/OneDrive/Desktop/communication sys/emails.csv')
    senders_df = pd.read_csv('C:/Users/Ban/OneDrive/Desktop/communication sys/senders-emails.csv')
    st.success(f"✅ Receivers loaded: **{len(receivers_df)}** | Senders loaded: **{len(senders_df)}**")
except Exception as e:
    st.error(f"❌ Error loading CSV files: {e}")
    st.stop()

# ---------- Method ----------
method = st.selectbox("📤 Choose Sending Method", ["Email", "WhatsApp"])
delay = 2

# ---------- Message Input ----------
if method == "Email":
    subject = st.text_input("📌 Email Subject", "Test Email")
    body_template = st.text_area("💌 Email Body", "Hello {name},\nThis is a test email from my project!")
else:
    subject = None
    body_template = st.text_area("💬 WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")

# ---------- Filter by Department ----------
if "dept" in receivers_df.columns:
    departments = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected_depts = st.multiselect("🏢 Choose Department(s)", options=departments, default=departments)

    if not selected_depts:
        st.warning("⚠️ No department selected, sending to all.")
        filtered_df = receivers_df
    else:
        filtered_df = receivers_df[receivers_df["dept"].isin(selected_depts)]
        st.info(f"📋 {len(filtered_df)} receiver(s) found in selected department(s).")
else:
    st.error("❌ 'dept' column not found in receivers file!")
    filtered_df = receivers_df

# ---------- WhatsApp Numbers ----------
if method == "WhatsApp":
    if "number" not in filtered_df.columns:
        st.error("❌ 'number' column not found in receivers file!")
        st.stop()
    whatsapp_numbers = filtered_df["number"].tolist()

# ---------- Send Button ----------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages Now"):
    st.success("✨ Sending started instantly!", icon="⚡")

    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))
    api = EvolutionAPI()

    for _, row in filtered_df.iterrows():
        name = row["name"]
        message = body_template.format(name=name)
        try:
            if method == "Email":
                sender_data = next(senders_cycle)
                sender_email = sender_data["email"]
                app_password = sender_data["app_password"]
                receiver = row["email"]

                msg = MIMEText(message)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = receiver

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()
            else:
                number = str(row["number"]).strip()
                api.send_message(number, message)

            sent_count += 1
        except Exception as e:
            st.error(f"❌ Failed for {name}: {e}")

        time.sleep(delay)

    st.success(f"🎉 Done! {sent_count}/{total} messages sent successfully.", icon="✅")

# ---------- Footer ----------


st.markdown("</div>", unsafe_allow_html=True)
