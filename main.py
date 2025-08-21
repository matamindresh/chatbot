import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from prometheus_flask_exporter import PrometheusMetrics


os.environ["DEBUG_METRICS"] = "1"
app = Flask(__name__)
CORS(app)

metrics = PrometheusMetrics(app, path='/metrics')  

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chatbot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_input = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()


API_KEY = os.getenv("API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate_text():
    if not API_KEY:
        return jsonify({"error": "API key not set"}), 500

    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        # Get last 5 conversations
        history = Conversation.query.order_by(Conversation.id.desc()).limit(5).all()
        history = list(reversed(history))

        messages = []
        for h in history:
            messages.append({"role": "user", "parts": [{"text": h.user_input}]})
            messages.append({"role": "model", "parts": [{"text": h.bot_response}]})
        messages.append({"role": "user", "parts": [{"text": prompt}]})

        payload = {"contents": messages}
        headers = {"Content-Type": "application/json"}
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        if result.get("candidates"):
            text_response = result["candidates"][0]["content"]["parts"][0]["text"]

            convo = Conversation(user_input=prompt, bot_response=text_response)
            db.session.add(convo)
            db.session.commit()

            return jsonify({"response": text_response})
        else:
            return jsonify({"error": "No response generated"}), 500

    except Exception as e:
        return jsonify({"error": f"Failed: {str(e)}"}), 500

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    conversations = Conversation.query.order_by(Conversation.id.desc()).all()
    return jsonify([
        {
            "id": c.id,
            "user_input": c.user_input,
            "bot_response": c.bot_response,
            "timestamp": c.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for c in conversations
    ])

@app.route('/debug/routes')
def show_routes():
    return str(app.url_map)

if __name__ == '__main__':
    print("Registered routes:", app.url_map)  # should include /metrics
    app.run(host="0.0.0.0", port=5000, debug=True)
