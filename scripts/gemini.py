import requests
import os
import time

output_dir = "source/gemini"

def process(id, prompt, regenerate=False):

    if not regenerate and os.path.exists(f'{output_dir}/{id}.txt'):
        with open(f'{output_dir}/{id}.txt', 'r') as f:
            return f.read()

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
    text = response.json()['candidates'][0]['content']['parts'][0]['text']
    # Limit to 15 requests per minute
    time.sleep(4)
    with open(f'{output_dir}/{id}.txt', 'w') as f:
        f.write(text)
    return text