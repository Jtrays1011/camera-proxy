from flask import Flask, request, jsonify
import requests
import openai
import os
import base64

# Initialize Flask app
app = Flask(__name__)

# Set your OpenAI key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

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

        # Handle text or image input
        user_text = data.get("text")
        image_data = data.get("image")

        if not user_text and not image_data:
            return jsonify({"error": "Missing text or image data"}), 400

        # --- If text provided ---
        if user_text:
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an AI assistant inside a calculator. Keep responses short and clear."},
                    {"role": "user", "content": user_text}
                ]
            )
            response_text = completion.choices[0].message["content"]
            return jsonify({"response": response_text}), 200

        # --- If image provided (base64 encoded) ---
        if image_data:
            image_bytes = base64.b64decode(image_data)
            image_path = "/tmp/input.jpg"
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            # Call OpenAI Vision model
            vision_response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": "Describe or solve what’s in this image."},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
                    ]}
                ]
            )

            vision_text = vision_response.choices[0].message["content"]
            return jsonify({"response": vision_text}), 200

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


# Run locally (Render ignores this, gunicorn handles it)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
