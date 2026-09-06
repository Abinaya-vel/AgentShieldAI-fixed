from flask import Flask, jsonify, render_template, request
from analyzer import analyze_content
import os

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "AgentShield AI",
        "version": "1.0.0"
    })

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must use JSON format."}), 400

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "Invalid request body."}), 400

        text = data.get("text")
        if not isinstance(text, str):
            return jsonify({"error": "The 'text' field must be a string."}), 400

        text = text.strip()
        if not text:
            return jsonify({"error": "Please provide content to analyze."}), 400

        if len(text) > 5000:
            return jsonify({"error": "Content cannot exceed 5000 characters."}), 413

        return jsonify(analyze_content(text)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except Exception as error:
        print(f"[AgentShield] Server error: {error}")
        return jsonify({
            "error": "An unexpected error occurred while analyzing the content."
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=True
    )
