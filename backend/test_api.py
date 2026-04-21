"""
Quick test script to verify all backend APIs are working.
Run this AFTER starting the server: python app.py
Usage: python test_api.py
"""

import requests
import json

BASE = "http://localhost:5000/api"

def test(name, method, url, data=None):
    """Helper to test an API endpoint."""
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"{method} {url}")
    try:
        if method == "GET":
            r = requests.get(url, timeout=10)
        elif method == "POST":
            r = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            r = requests.put(url, json=data, timeout=10)
        elif method == "DELETE":
            r = requests.delete(url, timeout=10)
        
        print(f"Status: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)[:500]}")
        return r.json()
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


if __name__ == '__main__':
    print("=" * 50)
    print("  OFFLINE AI CHATBOT — API TEST SUITE")
    print("=" * 50)

    # 1. Status check
    test("Health Check", "GET", f"{BASE}/status")

    # 2. Chat
    test("Send Chat Message", "POST", f"{BASE}/chat", {"message": "Hello, what can you do?"})

    # 3. Chat History
    test("Get Chat History", "GET", f"{BASE}/history?limit=5")

    # 4. GPS - Save
    test("Save GPS Location", "POST", f"{BASE}/gps", {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "accuracy": 10.5,
        "label": "Test Location"
    })

    # 5. GPS - Get
    test("Get GPS Locations", "GET", f"{BASE}/gps?limit=5")

    # 6. GPS - Latest
    test("Get Latest GPS", "GET", f"{BASE}/gps?latest=true")

    # 7. Emergency Contacts
    test("Get Emergency Contacts", "GET", f"{BASE}/emergency")

    # 8. Add Emergency Contact
    test("Add Emergency Contact", "POST", f"{BASE}/emergency", {
        "name": "Test Hospital",
        "phone": "102",
        "description": "Nearest hospital",
        "lat": 28.6200,
        "lon": 77.2150,
        "category": "medical"
    })

    # 9. Radio Channels
    test("Get Radio Channels", "GET", f"{BASE}/radio")

    # 10. Add Radio Channel
    test("Add Radio Channel", "POST", f"{BASE}/radio", {
        "name": "Test Channel",
        "frequency": "100.5 MHz",
        "description": "Test broadcast"
    })

    # 11. Notes - Create
    test("Create Note", "POST", f"{BASE}/notes", {
        "title": "Emergency Plan",
        "content": "Meet at point A if separated.",
        "category": "emergency"
    })

    # 12. Notes - Get All
    test("Get All Notes", "GET", f"{BASE}/notes")

    print("\n" + "=" * 50)
    print("  ALL TESTS COMPLETED")
    print("=" * 50)
