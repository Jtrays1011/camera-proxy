from flask import Flask, request, jsonify
import requests
import base64
import os

app = Flask(__name__)

# ===============================
# 🔐 OpenAI API Key (set this in Replit Secrets)
# ===============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Add it in Secrets tab

# ===============================
# 🔧 Helper function to send to OpenAI
# ===============================
def analyze_image_with_openai(image_b64):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image in one short sentence."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
                ]
            }
        ]
    }

    try:
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        res.raise_for_status()
        reply = res.json()
        message = reply["choices"][0]["message"]["content"]
        return message
    except Exception as e:
        print("❌ Error communicating with OpenAI:", e)
        return "Error contacting OpenAI."

# ===============================
# 🌐 Flask endpoint
# ===============================
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        img_data = request.json.get("image_b64")
        if not img_data:
            return jsonify({"error": "No image data provided"}), 400

        result = analyze_image_with_openai(img_data)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# 🧠 Root route (test connection)
# ===============================
@app.route('/')
def index():
    return "✅ Replit OpenAI Proxy is running!"

# ===============================
# 🚀 Start server
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
