"""
OFFLINE AI CHATBOT + GPS SYSTEM — Backend Server
=================================================
A completely offline Flask backend that provides:
  1. /api/chat        — AI chatbot via Ollama (offline LLM)
  2. /api/gps         — GPS location storage & retrieval
  3. /api/radio       — Offline radio / audio broadcast system
  4. /api/notes       — Offline notes storage
  5. /api/emergency   — Emergency contacts management
  6. /api/history     — Chat history retrieval
  7. /api/status      — Health check endpoint

Tech Stack: Python, Flask, SQLite, Ollama
Models: TinyLlama / Mistral / Phi-2 (configurable)
All data stored locally in SQLite — zero internet required.
"""

import os
import sqlite3
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# ─────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'chatbot.db')
OLLAMA_URL = 'http://localhost:11434/api/chat'
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'tinyllama')  # Change to 'mistral' or 'phi' as needed

# Flask App Setup
app = Flask(__name__)
CORS(app)  # Allow frontend from any origin to connect


# ─────────────────────────────────────────────
# Database Initialization
# ─────────────────────────────────────────────
def get_db():
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize all database tables."""
    conn = get_db()
    cursor = conn.cursor()

    # Chat messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # GPS locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            accuracy REAL,
            label TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Emergency contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            lat REAL,
            lon REAL,
            phone TEXT,
            category TEXT DEFAULT 'general'
        )
    ''')

    # Notes table (offline notepad feature)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            category TEXT DEFAULT 'general',
            is_pinned INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Radio channels / audio broadcast table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS radio_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            frequency TEXT,
            description TEXT,
            audio_file TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed default emergency contacts if empty
    cursor.execute('SELECT COUNT(*) as cnt FROM emergency_contacts')
    if cursor.fetchone()['cnt'] == 0:
        default_contacts = [
            ('Police', 'Emergency Police Services', 28.6139, 77.2090, '100', 'police'),
            ('Ambulance', 'Emergency Medical Services', 28.6129, 77.2080, '108', 'medical'),
            ('Fire Brigade', 'Fire Emergency Services', 28.6149, 77.2100, '101', 'fire'),
            ('Disaster Helpline', 'National Disaster Response', 28.6159, 77.2110, '1078', 'disaster'),
            ('Women Helpline', 'Women Safety Helpline', 28.6119, 77.2070, '1091', 'safety'),
        ]
        cursor.executemany(
            'INSERT INTO emergency_contacts (name, description, lat, lon, phone, category) VALUES (?, ?, ?, ?, ?, ?)',
            default_contacts
        )

    # Seed default radio channels if empty
    cursor.execute('SELECT COUNT(*) as cnt FROM radio_channels')
    if cursor.fetchone()['cnt'] == 0:
        default_channels = [
            ('Emergency Broadcast', '91.1 MHz', 'Local emergency broadcast channel', None, 1),
            ('Weather Updates', '98.3 MHz', 'Offline weather information relay', None, 1),
            ('Community Radio', '107.8 MHz', 'Community broadcast & announcements', None, 1),
            ('Rescue Coordination', '145.5 MHz', 'Search and rescue coordination', None, 1),
        ]
        cursor.executemany(
            'INSERT INTO radio_channels (name, frequency, description, audio_file, is_active) VALUES (?, ?, ?, ?, ?)',
            default_channels
        )

    conn.commit()
    conn.close()
    print("[OK] Database initialized successfully.")


# ─────────────────────────────────────────────
# Helper: Query Ollama (Offline AI Model)
# ─────────────────────────────────────────────
def query_ollama(messages):
    """Send messages to Ollama and get AI response. Fully offline."""
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": messages,
            "stream": False
        }
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get('message', {}).get('content', 'Sorry, I could not process that.')
    except requests.exceptions.ConnectionError:
        return "[WARNING] Ollama is not running. Start it with: ollama serve"
    except requests.exceptions.Timeout:
        return "[WARNING] AI model timed out. Try a shorter message or check if the model is loaded."
    except Exception as e:
        print(f"Ollama Error: {e}")
        return f"[ERROR] AI Error: {str(e)}"


# ═══════════════════════════════════════════════
# API ROUTES
# ═══════════════════════════════════════════════

# ─────────────────────────────────────────────
# 1. HEALTH CHECK / STATUS
# ─────────────────────────────────────────────
@app.route('/api/status', methods=['GET'])
def status():
    """Check if the backend and Ollama are running."""
    ollama_status = "offline"
    try:
        r = requests.get('http://localhost:11434/api/tags', timeout=3)
        if r.status_code == 200:
            ollama_status = "online"
            models = [m['name'] for m in r.json().get('models', [])]
        else:
            models = []
    except Exception:
        models = []

    return jsonify({
        'status': 'running',
        'ollama': ollama_status,
        'model': OLLAMA_MODEL,
        'available_models': models,
        'database': 'connected',
        'timestamp': datetime.now().isoformat()
    })


# ─────────────────────────────────────────────
# 2. CHAT API (Ollama AI)
# ─────────────────────────────────────────────
@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Send a message to the offline AI model.
    
    Request Body:
        { "message": "your question here" }
    
    Response:
        { "response": "AI answer", "timestamp": "..." }
    """
    data = request.json
    if not data or not data.get('message', '').strip():
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message'].strip()

    conn = get_db()
    cursor = conn.cursor()

    # Save user message
    cursor.execute(
        'INSERT INTO chats (role, content) VALUES (?, ?)',
        ('user', user_message)
    )

    # Get recent chat history for context (last 20 messages)
    cursor.execute(
        'SELECT role, content FROM chats ORDER BY id DESC LIMIT 20'
    )
    history = cursor.fetchall()[::-1]

    # Build messages list for Ollama
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful offline AI assistant designed for emergency and low-network situations. "
                "You can help with first aid, navigation, survival tips, and general questions. "
                "Keep responses concise, clear, and practical. "
                "If asked about location, guide the user to use the GPS feature. "
                "If asked about communication, guide the user to the Radio feature."
            )
        }
    ]
    messages.extend([{"role": row['role'], "content": row['content']} for row in history])

    # Get AI response
    bot_response = query_ollama(messages)

    # Save bot response
    cursor.execute(
        'INSERT INTO chats (role, content) VALUES (?, ?)',
        ('assistant', bot_response)
    )
    conn.commit()

    timestamp = datetime.now().isoformat()
    conn.close()

    return jsonify({
        'response': bot_response,
        'timestamp': timestamp
    })


@app.route('/api/chat/clear', methods=['POST'])
def clear_chat():
    """Clear all chat history."""
    conn = get_db()
    conn.execute('DELETE FROM chats')
    conn.commit()
    conn.close()
    return jsonify({'status': 'Chat history cleared'})


# ─────────────────────────────────────────────
# 3. CHAT HISTORY
# ─────────────────────────────────────────────
@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Get all chat history.
    
    Query Params:
        ?limit=50  — number of messages to return (default: 50)
    
    Response:
        { "history": [ { "role": "...", "content": "...", "timestamp": "..." }, ... ] }
    """
    limit = request.args.get('limit', 50, type=int)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT role, content, timestamp FROM chats ORDER BY id ASC LIMIT ?',
        (limit,)
    )
    chats = cursor.fetchall()
    conn.close()

    results = [
        {"role": row['role'], "content": row['content'], "timestamp": row['timestamp']}
        for row in chats
    ]
    return jsonify({'history': results, 'count': len(results)})


# ─────────────────────────────────────────────
# 4. GPS API
# ─────────────────────────────────────────────
@app.route('/api/gps', methods=['POST'])
def save_gps():
    """
    Save a GPS location.
    
    Request Body:
        { "latitude": 28.6139, "longitude": 77.2090, "accuracy": 10.5, "label": "Home" }
    
    Response:
        { "status": "saved", "id": 1, ... }
    """
    data = request.json
    lat = data.get('latitude')
    lon = data.get('longitude')
    accuracy = data.get('accuracy')
    label = data.get('label', '')

    if lat is None or lon is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO locations (latitude, longitude, accuracy, label) VALUES (?, ?, ?, ?)',
        (lat, lon, accuracy, label)
    )
    loc_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'status': 'saved',
        'id': loc_id,
        'latitude': lat,
        'longitude': lon,
        'accuracy': accuracy,
        'label': label,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/gps', methods=['GET'])
def get_gps():
    """
    Get saved GPS locations.
    
    Query Params:
        ?limit=10  — number of locations to return (default: 10)
        ?latest=true — get only the most recent location
    
    Response:
        { "locations": [ { "id": 1, "latitude": ..., ... }, ... ] }
    """
    latest = request.args.get('latest', 'false').lower() == 'true'
    limit = request.args.get('limit', 10, type=int)

    conn = get_db()
    cursor = conn.cursor()

    if latest:
        cursor.execute('SELECT * FROM locations ORDER BY id DESC LIMIT 1')
    else:
        cursor.execute('SELECT * FROM locations ORDER BY id DESC LIMIT ?', (limit,))

    locations = cursor.fetchall()
    conn.close()

    results = [
        {
            "id": row['id'],
            "latitude": row['latitude'],
            "longitude": row['longitude'],
            "accuracy": row['accuracy'],
            "label": row['label'],
            "timestamp": row['timestamp']
        }
        for row in locations
    ]

    return jsonify({'locations': results, 'count': len(results)})


@app.route('/api/gps/<int:loc_id>', methods=['DELETE'])
def delete_gps(loc_id):
    """Delete a specific GPS location."""
    conn = get_db()
    conn.execute('DELETE FROM locations WHERE id = ?', (loc_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': loc_id})


# ─────────────────────────────────────────────
# 5. RADIO API (Offline Radio / Audio Channels)
# ─────────────────────────────────────────────
@app.route('/api/radio', methods=['GET'])
def get_radio_channels():
    """
    Get all radio channels.
    
    Response:
        { "channels": [ { "id": 1, "name": "...", "frequency": "...", ... }, ... ] }
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM radio_channels ORDER BY id ASC')
    channels = cursor.fetchall()
    conn.close()

    results = [
        {
            "id": row['id'],
            "name": row['name'],
            "frequency": row['frequency'],
            "description": row['description'],
            "audio_file": row['audio_file'],
            "is_active": bool(row['is_active']),
            "created_at": row['created_at']
        }
        for row in channels
    ]
    return jsonify({'channels': results, 'count': len(results)})


@app.route('/api/radio', methods=['POST'])
def add_radio_channel():
    """
    Add a new radio channel.
    
    Request Body:
        { "name": "Channel Name", "frequency": "91.1 MHz", "description": "..." }
    """
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Channel name is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO radio_channels (name, frequency, description, audio_file, is_active) VALUES (?, ?, ?, ?, ?)',
        (
            data['name'],
            data.get('frequency', ''),
            data.get('description', ''),
            data.get('audio_file'),
            1
        )
    )
    channel_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'status': 'created', 'id': channel_id}), 201


@app.route('/api/radio/<int:channel_id>', methods=['PUT'])
def update_radio_channel(channel_id):
    """Update a radio channel."""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    # Check if channel exists
    cursor.execute('SELECT id FROM radio_channels WHERE id = ?', (channel_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Channel not found'}), 404

    cursor.execute(
        '''UPDATE radio_channels 
           SET name = COALESCE(?, name),
               frequency = COALESCE(?, frequency),
               description = COALESCE(?, description),
               is_active = COALESCE(?, is_active)
           WHERE id = ?''',
        (
            data.get('name'),
            data.get('frequency'),
            data.get('description'),
            data.get('is_active'),
            channel_id
        )
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'updated', 'id': channel_id})


@app.route('/api/radio/<int:channel_id>', methods=['DELETE'])
def delete_radio_channel(channel_id):
    """Delete a radio channel."""
    conn = get_db()
    conn.execute('DELETE FROM radio_channels WHERE id = ?', (channel_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': channel_id})


# ─────────────────────────────────────────────
# 6. EMERGENCY CONTACTS API
# ─────────────────────────────────────────────
@app.route('/api/emergency', methods=['GET'])
def get_emergency_contacts():
    """
    Get all emergency contacts.
    
    Query Params:
        ?category=police  — filter by category
    
    Response:
        { "contacts": [ { "id": 1, "name": "...", ... }, ... ] }
    """
    category = request.args.get('category')

    conn = get_db()
    cursor = conn.cursor()

    if category:
        cursor.execute(
            'SELECT * FROM emergency_contacts WHERE category = ? ORDER BY name',
            (category,)
        )
    else:
        cursor.execute('SELECT * FROM emergency_contacts ORDER BY name')

    contacts = cursor.fetchall()
    conn.close()

    results = [
        {
            "id": row['id'],
            "name": row['name'],
            "description": row['description'],
            "latitude": row['lat'],
            "longitude": row['lon'],
            "phone": row['phone'],
            "category": row['category']
        }
        for row in contacts
    ]
    return jsonify({'contacts': results, 'count': len(results)})


@app.route('/api/emergency', methods=['POST'])
def add_emergency_contact():
    """
    Add a new emergency contact.
    
    Request Body:
        { "name": "Hospital", "phone": "102", "description": "...", "lat": 28.6, "lon": 77.2, "category": "medical" }
    """
    data = request.json
    if not data or not data.get('name'):
        return jsonify({'error': 'Contact name is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO emergency_contacts (name, description, lat, lon, phone, category) VALUES (?, ?, ?, ?, ?, ?)',
        (
            data['name'],
            data.get('description', ''),
            data.get('lat'),
            data.get('lon'),
            data.get('phone', ''),
            data.get('category', 'general')
        )
    )
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'status': 'created', 'id': contact_id}), 201


@app.route('/api/emergency/<int:contact_id>', methods=['PUT'])
def update_emergency_contact(contact_id):
    """Update an emergency contact."""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM emergency_contacts WHERE id = ?', (contact_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Contact not found'}), 404

    cursor.execute(
        '''UPDATE emergency_contacts 
           SET name = COALESCE(?, name),
               description = COALESCE(?, description),
               lat = COALESCE(?, lat),
               lon = COALESCE(?, lon),
               phone = COALESCE(?, phone),
               category = COALESCE(?, category)
           WHERE id = ?''',
        (
            data.get('name'),
            data.get('description'),
            data.get('lat'),
            data.get('lon'),
            data.get('phone'),
            data.get('category'),
            contact_id
        )
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'updated', 'id': contact_id})


@app.route('/api/emergency/<int:contact_id>', methods=['DELETE'])
def delete_emergency_contact(contact_id):
    """Delete an emergency contact."""
    conn = get_db()
    conn.execute('DELETE FROM emergency_contacts WHERE id = ?', (contact_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': contact_id})


# ─────────────────────────────────────────────
# 7. NOTES API (Offline Notepad)
# ─────────────────────────────────────────────
@app.route('/api/notes', methods=['GET'])
def get_notes():
    """
    Get all notes.
    
    Query Params:
        ?category=general  — filter by category
        ?pinned=true       — get only pinned notes
    
    Response:
        { "notes": [ { "id": 1, "title": "...", ... }, ... ] }
    """
    category = request.args.get('category')
    pinned = request.args.get('pinned', 'false').lower() == 'true'

    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM notes'
    params = []
    conditions = []

    if category:
        conditions.append('category = ?')
        params.append(category)
    if pinned:
        conditions.append('is_pinned = 1')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY is_pinned DESC, updated_at DESC'

    cursor.execute(query, params)
    notes = cursor.fetchall()
    conn.close()

    results = [
        {
            "id": row['id'],
            "title": row['title'],
            "content": row['content'],
            "category": row['category'],
            "is_pinned": bool(row['is_pinned']),
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        }
        for row in notes
    ]
    return jsonify({'notes': results, 'count': len(results)})


@app.route('/api/notes', methods=['POST'])
def add_note():
    """
    Create a new note.
    
    Request Body:
        { "title": "My Note", "content": "Note content...", "category": "general" }
    """
    data = request.json
    if not data or not data.get('title', '').strip():
        return jsonify({'error': 'Note title is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notes (title, content, category) VALUES (?, ?, ?)',
        (
            data['title'].strip(),
            data.get('content', ''),
            data.get('category', 'general')
        )
    )
    note_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'status': 'created', 'id': note_id}), 201


@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """Update a note."""
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM notes WHERE id = ?', (note_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Note not found'}), 404

    cursor.execute(
        '''UPDATE notes 
           SET title = COALESCE(?, title),
               content = COALESCE(?, content),
               category = COALESCE(?, category),
               is_pinned = COALESCE(?, is_pinned),
               updated_at = CURRENT_TIMESTAMP
           WHERE id = ?''',
        (
            data.get('title'),
            data.get('content'),
            data.get('category'),
            data.get('is_pinned'),
            note_id
        )
    )
    conn.commit()
    conn.close()

    return jsonify({'status': 'updated', 'id': note_id})


@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """Delete a note."""
    conn = get_db()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'deleted', 'id': note_id})


# ═══════════════════════════════════════════════
# Run Server
# ═══════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  OFFLINE AI CHATBOT + GPS SYSTEM")
    print("  Backend Server Starting...")
    print(f"  Model: {OLLAMA_MODEL}")
    print(f"  Database: {DB_FILE}")
    print("=" * 50)
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
