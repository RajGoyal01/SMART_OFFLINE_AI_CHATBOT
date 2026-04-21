# 🛡️ OFFLINE AI CHATBOT + GPS SYSTEM

> **An emergency-grade offline application that works without internet.**
> Designed for war zones, disaster areas, and low-network environments where internet is the first thing to go down.

---

## 📌 Overview

This is the **backend server** for an offline AI chatbot with GPS tracking, radio channels, notes, and emergency contacts. Everything runs locally on the device — **zero internet required**.

## ⚙️ Tech Stack

| Component      | Technology           | Why Offline?                         |
|----------------|----------------------|--------------------------------------|
| Backend        | Python + Flask       | Runs on localhost, no cloud needed   |
| AI Model       | Ollama (TinyLlama)   | LLM runs entirely on device          |
| Database       | SQLite               | File-based DB, no server needed      |
| GPS            | Device GPS sensor    | Hardware GPS, no internet needed     |
| Radio          | Local audio channels | Pre-loaded channels, offline storage |

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
# Then pull a lightweight model:
ollama pull tinyllama
```

### Step 3: Run the Server
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
  "model": "tinyllama",
  "available_models": ["tinyllama:latest"],
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
| OLLAMA_MODEL  | `tinyllama`  | Change AI model (env variable) |
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

1. **No Internet Needed** — Everything runs on localhost
2. **No Cloud** — AI model is on your device via Ollama
3. **No External DB** — SQLite is just a file on disk
4. **GPS Works Offline** — Uses device hardware GPS sensor
5. **Radio Channels** — Pre-loaded offline audio/frequency data
6. **LAN Access** — Multiple devices can connect via local WiFi (router without internet)
7. **Lightweight** — TinyLlama runs on 4GB RAM laptops

---

## 👥 Team

- **Backend**: [Your Name]
- **Frontend**: [Friend's Name]
