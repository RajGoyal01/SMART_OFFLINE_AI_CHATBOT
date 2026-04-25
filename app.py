import streamlit as st

# ---------- PAGE CONFIG (MUST BE FIRST) ----------
st.set_page_config(
    page_title="R4 Rescue System",
    page_icon="🛰️",
    layout="centered"
)

import time
import uuid
import random

from encryption import encrypt, decrypt
from ai_module import generate_response, detect_intent
from database import init_db, save_message, get_messages_for_device

# ---------- INIT ----------
init_db()

# ---------- STATE ----------
if "device" not in st.session_state:
    st.session_state.device = "Device A"

if "mode" not in st.session_state:
    st.session_state.mode = "INTERNET"

if "send_mode" not in st.session_state:
    st.session_state.send_mode = "Direct"

if "model" not in st.session_state:
    st.session_state.model = "phi"

if "input_box" not in st.session_state:
    st.session_state.input_box = ""

# ---------- HEADER ----------
st.title("🛰️ R4 Rescue System")
st.caption("Secure Emergency Communication Interface")

col1, col2 = st.columns(2)

with col1:
    st.session_state.device = st.selectbox("Device", ["Device A", "Device B"])

with col2:
    st.session_state.mode = st.radio("Network Mode", ["MESH", "INTERNET"])

st.session_state.send_mode = st.selectbox("Send Mode", ["Direct", "Broadcast"])
st.session_state.model = st.selectbox("AI Model", ["phi", "mistral", "llama3"])

st.success(f"{st.session_state.device} ACTIVE | {st.session_state.mode}")

st.markdown("---")

# ---------- GOVERNMENT BROADCAST ----------
st.markdown("### 📢 Government Broadcast")

if st.button("🚨 Send Government Alert"):
    msg = "⚠ Government Alert: Stay indoors and follow official instructions"

    save_message({
        "id": str(uuid.uuid4())[:8],
        "sender": "GOV",
        "receiver": "ALL",
        "time": time.strftime("%H:%M:%S"),
        "encrypted": encrypt(msg),
        "priority": "EMERGENCY",
        "mode": "SYSTEM",
        "signal": "ALL",
        "emergency": True
    })

    st.success("Broadcast sent")

st.markdown("---")

# ---------- QUICK ACTIONS ----------
st.markdown("### ⚡ Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("TEST NORMAL"):
        st.session_state.input_box = "Hello, status check"
        st.rerun()

with col2:
    if st.button("TEST EMERGENCY"):
        st.session_state.input_box = "HELP I AM INJURED"
        st.rerun()

# ---------- PREDEFINED ----------
st.markdown("### 🎯 Predefined Queries")

predefined = st.selectbox(
    "Select scenario",
    [
        "None",
        "Who is the PM of India?",
        "What to do during a missile attack?",
        "How to treat bleeding injury?",
        "What is happening in war zones?",
        "Safety tips during explosion"
    ]
)

if predefined != "None":
    st.session_state.input_box = predefined

st.markdown("---")

# ---------- NETWORK ----------
def get_signal():
    return random.choice(["STRONG", "MEDIUM", "WEAK"])

def simulate_network(signal, emergency):
    if emergency:
        return True
    if signal == "WEAK":
        return random.choice([True, False])
    if signal == "MEDIUM":
        time.sleep(1)
    return True

def get_receiver(device, send_mode):
    if send_mode == "Broadcast":
        return "ALL"
    return "Device B" if device == "Device A" else "Device A"

# ---------- SEND ----------
def send_message():
    msg = st.session_state.get("input_box", "")
    if not msg.strip():
        return

    intent = detect_intent(msg)
    emergency = intent == "EMERGENCY"
    signal = get_signal()

    if not simulate_network(signal, emergency):
        st.warning("⚠ Message lost due to weak signal")
        return

    receiver = get_receiver(st.session_state.device, st.session_state.send_mode)

    data = {
        "id": str(uuid.uuid4())[:8],
        "sender": st.session_state.device,
        "receiver": receiver,
        "time": time.strftime("%H:%M:%S"),
        "encrypted": encrypt(msg),
        "priority": intent,
        "mode": st.session_state.mode,
        "signal": signal,
        "emergency": emergency
    }

    save_message(data)

    # ---------- AI RESPONSE ----------
    ai_reply = generate_response(msg, st.session_state.model)

    save_message({
        "id": str(uuid.uuid4())[:8],
        "sender": "AI",
        "receiver": st.session_state.device,
        "time": time.strftime("%H:%M:%S"),
        "encrypted": encrypt(ai_reply),
        "priority": "AI",
        "mode": "AI",
        "signal": "N/A",
        "emergency": False
    })

# ---------- INPUT ----------
with st.form("msg_form", clear_on_submit=True):
    st.text_input(
        "",
        key="input_box",
        value=st.session_state.input_box,
        placeholder="Type message..."
    )
    submitted = st.form_submit_button("Send")

    if submitted:
        send_message()

st.markdown("---")

# ---------- FETCH ----------
messages = get_messages_for_device(st.session_state.device)

# ---------- INBOX / OUTBOX (ADDED) ----------
inbox = [
    m for m in messages
    if m["receiver"] in [st.session_state.device, "ALL"]
]

outbox = [
    m for m in messages
    if m["sender"] == st.session_state.device
]

# ---------- RENDER ----------
def render(m):
    text = decrypt(m["encrypted"]).replace("<", "").replace(">", "")
    formatted = text.replace("\n", "<br>")

    enc = m["encrypted"]
    enc_preview = enc[:25] + "..." if len(enc) > 30 else enc

    color = {
        "EMERGENCY": "red",
        "CRISIS_INFO": "orange",
        "AI": "blue"
    }.get(m["priority"], "green")

    if m["sender"] == "GOV":
        color = "yellow"

    return f"""
    <div style="
        border:2px solid {color};
        padding:14px;
        margin:10px;
        border-radius:8px;
        background:#0a0f1a;
        color:white;
        font-family:monospace;
    ">
    
    <div style="display:flex; justify-content:space-between;">
        <b>{m['sender']}</b>
        <span>{m['time']}</span>
    </div>

    <br>

    <small>
    ID: {m['id']} | SIGNAL: {m['signal']} | TYPE: {m['priority']}
    </small>

    <hr style="border:0.5px solid gray;">

    <small style="color:#aaaaaa;">
    ENC: {enc_preview}
    </small>

    <br><br>

    <b>MSG:</b><br>
    {formatted}

    </div>
    """

# ---------- DISPLAY ----------
st.subheader("📥 INBOX")
for m in inbox:
    if st.session_state.mode == "MESH" and m["signal"] == "WEAK":
        continue
    st.markdown(render(m), unsafe_allow_html=True)

st.subheader("📤 OUTBOX")
for m in outbox:
    st.markdown(render(m), unsafe_allow_html=True)