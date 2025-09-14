import os
import openai
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import PyPDF2
from pptx import Presentation

# Load environment variables from .env file
load_dotenv()

# Configure the OpenAI API key
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("ERROR: OpenAI API Key not found.")

# Create Flask app
app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return render_template("index.html")   # or return "Hello, World!"

# Example route to talk with OpenAI (extend as needed)
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "")
    if not user_input:
        return jsonify({"error": "No question provided"}), 400

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        answer = response["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
