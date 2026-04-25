import requests

def detect_intent(message):
    msg = message.lower()

    if any(w in msg for w in ["injured","bleeding","sos","fire","attack","explosion"]):
        return "EMERGENCY"

    if any(w in msg for w in ["war","missile","conflict","bomb","army"]):
        return "CRISIS_INFO"

    return "GENERAL"

def generate_response(message, model="phi"):

    intent = detect_intent(message)

    if intent == "EMERGENCY":
        prompt = f"""
Emergency: {message}
Give exactly 3 short life-saving steps.
Each on new line.
"""

    elif intent == "CRISIS_INFO":
        prompt = f"""
Situation: {message}
Explain briefly and give 2-3 safety tips.
Use bullet points.
"""

    else:
        prompt = f"""
User: {message}
Give a clear short answer.
"""

    try:
        res = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=30
        )

        text = res.json().get("response", "").strip()

        if not text:
            return fallback(intent)

        return clean(text)

    except:
        if model != "phi":
            return generate_response(message, model="phi")

        return fallback(intent)

def clean(text):
    text = text.replace("<", "").replace(">", "")
    text = text.replace("1.", "\n1.")
    text = text.replace("2.", "\n2.")
    text = text.replace("3.", "\n3.")
    text = text.replace("- ", "\n- ")
    text = text.replace(". ", ".\n")
    return text.strip()

def fallback(intent):
    if intent == "EMERGENCY":
        return "1. STAY CALM\n2. APPLY FIRST AID\n3. SEEK HELP"
    elif intent == "CRISIS_INFO":
        return "- Stay alert\n- Follow guidance\n- Stay safe"
    return "Unable to respond."