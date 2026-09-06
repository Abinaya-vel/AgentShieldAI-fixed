import os
import json
from dotenv import load_dotenv
from google import genai

# ============================================================
# Load .env from project folder
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_PATH)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

print("========================================")
print("AgentShield AI - Analyzer")
print("API KEY LOADED:", bool(GEMINI_API_KEY))
print("MODEL:", MODEL_NAME)
print("========================================")

# ============================================================
# Gemini Client
# ============================================================

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# Analyze Content
# ============================================================

def analyze_content(text):

    if not text or not text.strip():
        raise ValueError("Please provide content to analyze.")

    if client is None:
        raise ValueError(
            "Gemini API key is missing. Please check your .env file."
        )

    prompt = f"""
You are AgentShield AI, an advanced cybersecurity scam and phishing
detection assistant.

Analyze the following content carefully.

Check for:

1. Phishing
2. Scam
3. Fraud
4. Social engineering
5. Malicious or suspicious links
6. Urgent or threatening language
7. Requests for passwords, OTPs, money or personal information
8. Fake bank or company impersonation
9. Suspicious job offers
10. Fake delivery or payment messages

Return ONLY valid JSON.

Use exactly this structure:

{{
    "risk_level": "Low",
    "risk_score": 0,
    "summary": "Short explanation of the threat.",
    "findings": [
        "Finding 1",
        "Finding 2"
    ],
    "recommendations": [
        "Recommendation 1",
        "Recommendation 2"
    ]
}}

Rules:

- risk_level must be exactly: Low, Medium, High, or Critical.
- risk_score must be an integer from 0 to 100.
- findings must be a JSON array.
- recommendations must be a JSON array.
- Do not use Markdown.
- Do not use code fences.
- Return ONLY JSON.

Content to analyze:

{text}
"""

    try:

        # ========================================================
        # Gemini API Request
        # ========================================================

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json"
            }
        )

        result = response.text

        if not result:
            raise ValueError("Gemini returned an empty response.")

        result = result.strip()

        # ========================================================
        # Remove Markdown code fences if Gemini adds them
        # ========================================================

        if result.startswith("```json"):
            result = result[7:]

        elif result.startswith("```"):
            result = result[3:]

        if result.endswith("```"):
            result = result[:-3]

        result = result.strip()

        # ========================================================
        # Convert JSON string to Python dictionary
        # ========================================================

        data = json.loads(result)

        # ========================================================
        # Make sure required fields exist
        # ========================================================

        return {
            "risk_level": data.get("risk_level", "Medium"),
            "risk_score": int(data.get("risk_score", 50)),
            "summary": data.get(
                "summary",
                "The content was analyzed for potential security threats."
            ),
            "findings": data.get("findings", []),
            "recommendations": data.get("recommendations", [])
        }

    except json.JSONDecodeError as error:

        print("========================================")
        print("JSON ERROR:")
        print(error)
        print("Gemini response:")
        print(result if "result" in locals() else "No response")
        print("========================================")

        return {
            "risk_level": "Medium",
            "risk_score": 50,
            "summary": "The AI response could not be parsed correctly.",
            "findings": [
                "The AI returned an unexpected response format."
            ],
            "recommendations": [
                "Do not click suspicious links.",
                "Do not share passwords, OTPs or financial information."
            ]
        }

    except Exception as error:

        print("========================================")
        print("GEMINI API ERROR:")
        print(type(error).__name__)
        print(str(error))
        print("========================================")

        raise ValueError(
            f"Gemini API error: {str(error)}"
        )