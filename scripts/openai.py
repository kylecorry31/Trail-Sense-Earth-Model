import requests
import os
import time

output_dir = "source/openai"

def process(id, prompt, regenerate=False, response_format=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not regenerate and os.path.exists(f'{output_dir}/{id}.txt'):
        with open(f'{output_dir}/{id}.txt', 'r') as f:
            return f.read()

    with open('openai-api-key.txt', 'r') as f:
        api_key = f.read().strip()

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
    }

    if response_format is not None:
        data["response_format"] = response_format

    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Failed to process prompt: {response.status_code}, {response.text}")
    text = response.json()['choices'][0]['message']['content']
    with open(f'{output_dir}/{id}.txt', 'w') as f:
        f.write(text)
    return text