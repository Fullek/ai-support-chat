# app.py (simple, minimal, explained inline):
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import openai

# Load keys from env
openai.api_key = os.getenv('OPENAI_API_KEY')
# Optional: SENDGRID, GMAIL tokens for real integration

app = Flask(__name__, static_folder='static')

# Simple system prompt (change to match client tone)
SYSTEM_PROMPT = "You are a helpful customer support assistant for Acme Store. Answer politely and concisely. If unsure, ask one clarifying question."

# Helper: call LLM
def call_llm(user_message, temperature=0.0):
    messages = [
        {"role":"system","content":SYSTEM_PROMPT},
        {"role":"user","content":user_message}
    ]
    resp = openai.ChatCompletion.create(model='gpt-4o', messages=messages, temperature=temperature, max_tokens=400)
    return resp['choices'][0]['message']['content']

# --- Web chat endpoints ---
@app.route('/chat', methods=['GET'])
def chat_ui():
    # serve a small chat page
    return send_from_directory('static', 'index.html')

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json or {}
    user_text = data.get('message','')
    if not user_text:
        return jsonify({'error':'no message'}),400
    reply = call_llm(user_text)
    return jsonify({'reply':reply})

# --- Simulated email inbox (for demo without real Gmail setup) ---
INBOX = [
    {'id':1,'from':'customer1@example.com','subject':'Where is my order?','body':'I ordered on Nov 20 and still no tracking number.'},
    {'id':2,'from':'customer2@example.com','subject':'Return request','body':'I want to return item #1234, what is the process?'}
]

@app.route('/demo/inbox', methods=['GET'])
def demo_inbox():
  return jsonify(INBOX)

@app.route('/demo/process_email/<int:msg_id>', methods=['POST'])
def process_email(msg_id):
    msg = next((m for m in INBOX if m['id']==msg_id), None)
    if not msg:
        return jsonify({'error':'not found'}),404
    prompt = f"Customer email:\nFrom: {msg['from']}\nSubject: {msg['subject']}\nBody: {msg['body']}\n\nWrite a short polite reply with next steps and ask clarifying Q if needed." 
    reply = call_llm(prompt)
    # In real integration: send via Gmail API or create Zendesk ticket
    return jsonify({'reply':reply})

# Health
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status':'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT',3000))
    app.run(host='0.0.0.0', port=port)
