from flask import Flask, request, jsonify
from openai import OpenAI
import os
import base64

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def home():
    return jsonify({
        "status": "online",
        "message": "✅ Flask proxy is running and ready for ESP32 requests!"
    })

@app.route("/process", methods=["POST"])
def process():
    try:
        data = request.get_json()

        user_text = data.get("text")
        image_data = data.get("image")

        if not user_text and not image_data:
            return jsonify({"error": "Missing text or image data"}), 400

        # Text processing
        if user_text:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant inside a calculator. Keep responses short and clear."},
                    {"role": "user", "content": user_text}
                ]
            )
            response_text = completion.choices[0].message.content
            return jsonify({"response": response_text}), 200

        # Image processing
        if image_data:
            vision_completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe or solve what's in this image."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                        ]
                    }
                ]
            )
            vision_text = vision_completion.choices[0].message.content
            return jsonify({"response": vision_text}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
