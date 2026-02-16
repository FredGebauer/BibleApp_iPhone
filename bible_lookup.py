import requests

ESV_API_KEY = "7580d95a1be11f5097f01d04f98f6d6d999d2768"

headers = {
    "Authorization": f"Token {ESV_API_KEY}"
}


def lookup_verse(reference: str) -> str:
    reference = reference.strip()

    # Your existing API call logic here
    url = f"https://api.esv.org/v3/passage/text/?q={reference}"

    response = requests.get(url, headers=headers)
    data = response.json()

    return data["passages"][0]


def fetch_bible_verse(reference):
    params = {
        "q": reference,
        "include-passage-references": False,
        "include-footnotes": True,
        "include-headings": False,
        "include-verse-numbers": True,
        "include-short-copyright": False,
    }

    url = "https://api.esv.org/v3/passage/text/"

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return None, f"ESV API error: {e}"

    passages = data.get("passages")
    footnotes = data.get("footnotes", [])

    if not passages:
        return None, "No passage text returned from ESV API."

    verse_text = "\n".join(p.strip() for p in passages)

    if footnotes:
        verse_text += "\n\nESV FOOTNOTES:\n"
        for fn in footnotes:
            verse_text += f"- {fn}\n"

    return verse_text, data
