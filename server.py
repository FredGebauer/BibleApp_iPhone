import json
import requests
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# -----------------------------
#  ESV API LOOKUP
# -----------------------------
ESV_API_KEY = "7580d95a1be11f5097f01d04f98f6d6d999d2768"


def fetch_bible_verse(reference):
    url = "https://api.esv.org/v3/passage/text/"
    headers = {"Authorization": f"Token {ESV_API_KEY}"}

    params = {
        "q": reference,
        "include-passage-references": False,
        "include-verse-numbers": True,
        "include-first-verse-numbers": True,
        "include-footnotes": True,
        "include-footnote-body": True,
        "include-footnote-markers": True,
        "include-headings": False,
        "include-short-copyright": False,
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        passages = data.get("passages", [])
        footnotes = data.get("footnotes", [])

        if not passages:
            return "Verse not found."

        # Main verse text
        verse_text = passages[0].strip()

        # Add footnotes only if present
        if footnotes:
            verse_text += "\n\nFOOTNOTES:\n"
            for fn in footnotes:
                verse_text += f"- {fn}\n"

        return verse_text

    except Exception as e:
        return f"Error fetching verse: {e}"


# -----------------------------
#  SERVE INDEX.HTML
# -----------------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# -----------------------------
#  LOOKUP ROUTE
# -----------------------------
@app.route("/lookup")
def lookup():
    reference = request.args.get("reference", "").strip()

    # Get verse text (single return value)
    verse_text = fetch_bible_verse(reference)

    # Load interpretations.json
    try:
        with open("interpretations.json", "r") as f:
            interpretations = json.load(f)
    except:
        interpretations = {}

    # Flat string interpretation
    interp = interpretations.get(reference, {}).get("interpretation", "")

    # Return JSON that matches your HTML
    return jsonify({
        "reference": reference,
        "verse": reference,
        "verse_text": verse_text,
        "interpretation": interp
    })
# -----------------------------
#  SAVE INTERPRETATION
# -----------------------------


@app.route("/save_interpretation", methods=["POST"])
def save_interpretation():
    data = request.get_json()
    reference = data["reference"]
    interpretation = data["interpretation"]

    # Load existing interpretations
    try:
        with open("interpretations.json", "r") as f:
            interpretations = json.load(f)
    except:
        interpretations = {}

    # Save in your simple format
    interpretations[reference] = {
        "verse": reference,
        "interpretation": interpretation
    }

    # Write back to file
    with open("interpretations.json", "w") as f:
        json.dump(interpretations, f, indent=4)

    return jsonify({"status": "ok"})


# -----------------------------
#  RUN SERVER
# -----------------------------
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5005))
    app.run(host="0.0.0.0", port=port)
