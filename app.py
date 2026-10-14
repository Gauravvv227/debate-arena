from flask import Flask, request, Response
from flask_cors import CORS
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
@app.route("/api/argument", methods=["POST"])
def get_argument():
    data = request.get_json()
    topic = data.get("topic")
    side = data.get("side")
    round_num = data.get("round")
    history = data.get("history", [])

    own_side = side
    opponent = "against" if side == "for" else "for"

    own_history = [h for h in history if h["side"] == own_side]
    opponent_entries = [h for h in history if h["side"] == opponent]
    opponent_latest = opponent_entries[-1] if opponent_entries else None

    context = ""
    if own_history:
        own_text = " ".join(h["text"] for h in own_history)
        context += f'You already argued: "{own_text}". Do not repeat these points. '
    if opponent_latest:
        context += f'Your opponent just said: "{opponent_latest["text"]}". Briefly address their point, then bring in a new angle or piece of evidence for your side. '

    prompt = f'You are arguing {"FOR" if side == "for" else "AGAINST"} this statement: "{topic}". {context}Give round {round_num} of your argument. Be concise, sharp and persuasive. 2-3 sentences only.'

    def generate():
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-oss-20b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "stream": True
            },
            stream=True
        )

        for line in response.iter_lines():
            if line:
                yield line.decode("utf-8") + "\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)