from flask import Flask, request, jsonify
from openai import OpenAI
import json
import yaml
import os

with open ("config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

app = Flask(__name__)
client = OpenAI(api_key=cfg["api_key"]["key"])

def load_history():
    if not os.path.exists("storage.json"):
        return {}
    with open("storage.json", "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def save_history(history):
    with open("storage.json", "w") as f:
        json.dump(history, f, indent=2)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_name = data.get("name")
    user_message = data.get("message")

    history = load_history()

    if user_name not in history:
        history[user_name] = [
            {"role": "system", "content": "Você é um nutricionista amigável que acompanha a dieta do usuário e conversa de forma contínua."}
        ]

    history[user_name].append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model=cfg["model"]["name"],
        messages=history[user_name]
    )

    assistant_reply = response.choices[0].message.content

    history[user_name].append({"role": "assistant", "content": assistant_reply})

    save_history(history)

    return jsonify({"reply": assistant_reply, "history": history[user_name]})

if __name__ == "__main__":
    app.run(debug=True)
