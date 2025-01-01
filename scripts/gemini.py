import requests

def process(prompt):
    with open('google-gemini-api-key.txt', 'r') as f:
        api_key = f.read().strip()

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to process prompt: {response.status_code}, {response.text}")
    return response.json()['candidates'][0]['content']['parts'][0]['text']