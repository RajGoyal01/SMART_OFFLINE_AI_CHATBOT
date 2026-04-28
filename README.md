# 🛡️ OFFLINE AI CHATBOT + GPS SYSTEM

> **An emergency-grade offline application that works without internet.**
> Designed for war zones, disaster areas, and low-network environments where internet is the first thing to go down.

---

## 📌 Overview

This is the **backend server** for an offline AI chatbot with GPS tracking, radio channels, notes, and emergency contacts. Everything runs locally on the device — **zero internet required**.

---

## 🖥️ Hardware Requirements

| # | Component | Specification | Purpose |
|---|-----------|--------------|---------|
| 1 | **Raspberry Pi 5** | 8GB RAM | Edge client — runs the frontend UI and sends API requests to laptop over LAN |
| 2 | **Power Cables** | Pi 5 USB-C (27W) + Laptop adapter | Powers the Raspberry Pi and laptop |
| 3 | **HDMI Cable** | Micro-HDMI to HDMI | Connects Pi to the display screen |
| 4 | **Screen / Monitor** | Any HDMI-compatible display | Shows AI chat responses and GPS data |
| 5 | **SD Card** | 32GB (Class 10 / A2 recommended) | OS and app storage for the Pi |
| 6 | **GPS Module** | UART/USB GPS (e.g., Neo-6M / Neo-8M) | Offline hardware GPS — no internet needed |
| 7 | **LoRa Module** | SX1276 / SX1278 (433 MHz or 868/915 MHz) | Long-range offline radio communication between devices |

> 💡 **Tip:** Use a **Class 10 / A2-rated SD card** for significantly faster read/write speeds on the Pi.

> 📡 **LoRa Range:** LoRa modules can reach **2–15 km line-of-sight** — ideal for disaster/war-zone deployments where cellular networks are down.

---

## ⚙️ Tech Stack

| Component               | Technology             | Why Offline?                              |
|-------------------------|------------------------|-------------------------------------------|
| Backend                 | Python + Flask         | Runs on localhost, no cloud needed        |
| AI Model                | Ollama (Phi-3 Mini)    | LLM runs entirely on device               |
| Database                | SQLite                 | File-based DB, no server needed           |
| GPS                     | Hardware GPS module    | Hardware GPS, no internet needed          |
| Radio                   | LoRa Module            | Long-range offline radio comms            |
| Gas Detection           | Poisonous Gas Detector | Detects toxic gases locally, no cloud     |
| Radiation Detection     | Radiation Detector     | Measures radiation levels offline         |
| Human Heat Detection    | Heat / IR Sensor       | Detects human presence via infrared       |
| Night Vision            | Night Vision Camera    | Captures footage in zero-light conditions |

---

## 🔄 System Workflow

The system is split across two devices — a **Raspberry Pi** (lightweight display client) and a **Laptop** (compute node running Ollama). They talk over a local WiFi network with **no internet required**.

```
┌─────────────────────────────────┐
│         Raspberry Pi 5          │
│         (8GB RAM Client)        │
│                                 │
│  • Displays UI on HDMI screen   │
│  • Reads GPS module (Neo-6M)    │
│  • Sends/receives via LoRa      │
│  • Reads gas/radiation sensors  │
│  • Heat instinct + night vision │
│  • Runs JS frontend             │
└────────────┬────────────────────┘
             │
             │  📶 WiFi API Request (LAN only, no internet)
             ▼
┌─────────────────────────────────┐
│   Laptop — Python Flask Backend │
│                                 │
│  • Handles all API routes       │
│  • Manages SQLite database      │
│  • GPS, Notes, Contacts APIs    │
│  • Processes sensor data        │
└────────────┬────────────────────┘
             │
             │  🤖 Inference Request
             ▼
┌─────────────────────────────────┐
│      Ollama (Phi-3 Mini)        │
│     (Runs locally on Laptop)    │
│                                 │
│  • Fully offline LLM            │
│  • Handles all chat queries     │
└────────────┬────────────────────┘
             │
             │  ✅ AI Response
             ▼
┌─────────────────────────────────┐
│       Flask Backend             │
│   (Formats & returns response)  │
└────────────┬────────────────────┘
             │
             │  📡 Response sent back over WiFi (LAN)
             ▼
┌─────────────────────────────────┐
│       Raspberry Pi Screen       │
│    (Displays AI chat response)  │
└─────────────────────────────────┘
```

---

## 🚀 Quick Setup (One-Time, Needs Internet)

### Step 1: Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Install & Setup Ollama
```bash
# Download Ollama from https://ollama.com
# Then pull the Phi-3 Mini model:
ollama pull phi3:mini
```

### Step 3: Keep the Model Warm (Run Once After Boot)
```bash
ollama run phi3:mini
```
> This keeps Phi-3 Mini loaded in background memory — avoids cold-start delay on every request.

### Step 4: Run the Server
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start Backend
cd backend
python app.py
```

Server will start at: **http://localhost:5000**

> ⚠️ After initial setup, **everything works 100% offline**. No internet needed ever again.

---

## 📡 API Documentation (For Frontend Integration)

Base URL: `http://localhost:5000/api`

---

### 1. 🟢 Health Check
```
GET /api/status
```
**Response:**
```json
{
  "status": "running",
  "ollama": "online",
  "model": "phi3:mini",
  "available_models": ["phi3:mini"],
  "database": "connected",
  "timestamp": "2026-04-21T23:30:00"
}
```

---

### 2. 💬 Chat (AI Chatbot)

#### Send Message
```
POST /api/chat
Content-Type: application/json

{ "message": "What should I do in an earthquake?" }
```
**Response:**
```json
{
  "response": "During an earthquake, Drop, Cover, and Hold On...",
  "timestamp": "2026-04-21T23:30:00"
}
```

#### Get Chat History
```
GET /api/history?limit=50
```
**Response:**
```json
{
  "history": [
    { "role": "user", "content": "Hello", "timestamp": "..." },
    { "role": "assistant", "content": "Hi! How can I help?", "timestamp": "..." }
  ],
  "count": 2
}
```

#### Clear Chat History
```
POST /api/chat/clear
```

---

### 3. 📍 GPS (Offline Location)

#### Save Location
```
POST /api/gps
Content-Type: application/json

{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "accuracy": 10.5,
  "label": "Safe Point A"
}
```

#### Get Saved Locations
```
GET /api/gps?limit=10
GET /api/gps?latest=true
```

#### Delete Location
```
DELETE /api/gps/{id}
```

---

### 4. 📻 Radio (Offline Channels)

#### Get All Channels
```
GET /api/radio
```
**Response:**
```json
{
  "channels": [
    {
      "id": 1,
      "name": "Emergency Broadcast",
      "frequency": "91.1 MHz",
      "description": "Local emergency broadcast channel",
      "audio_file": null,
      "is_active": true
    }
  ],
  "count": 4
}
```

#### Add Channel
```
POST /api/radio
Content-Type: application/json

{ "name": "Relief Channel", "frequency": "99.9 MHz", "description": "Aid coordination" }
```

#### Update Channel
```
PUT /api/radio/{id}
Content-Type: application/json

{ "name": "Updated Name", "is_active": false }
```

#### Delete Channel
```
DELETE /api/radio/{id}
```

---

### 5. 🚨 Emergency Contacts

#### Get All Contacts
```
GET /api/emergency
GET /api/emergency?category=medical
```
**Categories:** `police`, `medical`, `fire`, `disaster`, `safety`, `general`

#### Add Contact
```
POST /api/emergency
Content-Type: application/json

{
  "name": "Field Hospital",
  "phone": "102",
  "description": "Mobile hospital unit",
  "lat": 28.62,
  "lon": 77.21,
  "category": "medical"
}
```

#### Update Contact
```
PUT /api/emergency/{id}
```

#### Delete Contact
```
DELETE /api/emergency/{id}
```

---

### 6. 📝 Notes (Offline Notepad)

#### Get All Notes
```
GET /api/notes
GET /api/notes?category=emergency
GET /api/notes?pinned=true
```

#### Create Note
```
POST /api/notes
Content-Type: application/json

{
  "title": "Evacuation Plan",
  "content": "Route: Gate A → Highway 5 → Safe Zone B",
  "category": "emergency"
}
```

#### Update Note
```
PUT /api/notes/{id}
Content-Type: application/json

{ "title": "Updated Title", "is_pinned": true }
```

#### Delete Note
```
DELETE /api/notes/{id}
```

---

## 📁 Project Structure

```
OFFLINE_AI/
├── backend/
│   ├── app.py              ← Main Flask server (all APIs)
│   ├── requirements.txt    ← Python dependencies
│   ├── test_api.py         ← API test script
│   └── chatbot.db          ← SQLite database (auto-created)
├── frontend/               ← (Your friend builds this)
│   ├── index.html
│   ├── style.css
│   └── app.js
└── README.md               ← This file
```

---

## 🔧 Configuration

| Variable      | Default      | Description                    |
|---------------|--------------|--------------------------------|
| OLLAMA_MODEL  | `phi3:mini`  | Change AI model (env variable) |
| Port          | `5000`       | Backend server port            |
| Host          | `0.0.0.0`    | Accessible from any device on LAN |

Change model:
```bash
set OLLAMA_MODEL=mistral    # Windows
export OLLAMA_MODEL=mistral # Linux/Mac
python app.py
```

---

## 🧪 Testing

```bash
# Start server first, then in another terminal:
cd backend
python test_api.py
```

---

## 🛡️ Why This Works in War/Disaster Zones

1. **No Internet Needed** — Everything runs on localhost / LAN
2. **No Cloud** — AI model (Phi-3 Mini) runs entirely on your laptop via Ollama
3. **No External DB** — SQLite is just a file on disk
4. **GPS Works Offline** — Uses hardware GPS module (Neo-6M / Neo-8M)
5. **LoRa Radio** — Long-range (2–15 km) offline device-to-device communication
6. **Gas & Radiation Detection** — Real-time environmental threat sensing, fully offline
7. **Human Heat Detection** — Detects survivors or threats via infrared in any condition
8. **Night Vision Camera** — Operational in complete darkness, no light source needed
9. **LAN Access** — Multiple devices can connect via local WiFi (router without internet)
10. **Lightweight** — Phi-3 Mini runs fast; Pi handles sensors & UI, laptop handles compute

---

## 👥 Team

| # | Name |
|---|------|
| 1 | **Rudransh Dixit** |
| 2 | **Raj Gupta** |
| 3 | **Mahi Gupta** |
| 4 | **Ritesh Singh** |
| 5 | **Ramnesh Kumar Sahu** |
