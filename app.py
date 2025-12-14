from flask import Flask, request, jsonify, send_from_directory
import os
import requests

app = Flask(__name__, static_folder="static")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = (
    "You are a helpful customer support assistant for an online store. "
    "Be polite, concise and helpful. If you are unsure, ask one clarifying question."
)

def call_groq(user_message):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "groq/compound",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.2
    }

    r = requests.post(url, headers=headers, json=payload, timeout=30)

    if r.status_code != 200:
        return f"[ERROR from Groq] {r.status_code}: {r.text}"

    data = r.json()
    return data["choices"][0]["message"]["content"]

@app.route("/")
def home():
    return send_from_directory("static", "index.html")

@app.route("/chat")
def chat():
    return send_from_directory("static", "index.html")

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json or {}
    user_text = data.get("message", "")
    if not user_text:
        return jsonify({"error": "Empty message"}), 400
    reply = call_groq(user_text)
    return jsonify({"reply": reply})

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
