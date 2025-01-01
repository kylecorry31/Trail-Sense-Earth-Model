import requests
import json
import os
from PIL import Image
import io
from .progress import progress
import time

source_dir = 'source/wikipedia'
headers = {'User-Agent': 'Trail Sense Bot (trailsense@protonmail.com)'}

thumbnail_override = {
    'Asparagus_officinalis': 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Illustration_Asparagus_officinalis0b.jpg'
}

def __make_request(path, is_json=True):
    response = requests.get(f'https://en.wikipedia.org/api/rest_v1{path}', headers=headers)
    if response.status_code != 200:
        raise Exception(f'Error: {response.status_code}, {response.text}')
    return response.json() if is_json else response.text

def __get_image(title, url):
    if not os.path.exists(f'{source_dir}/{title}.webp'):
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f'Error: {response.status_code}, {response.text}')
        image_bytes = response.content
        image = Image.open(io.BytesIO(image_bytes))
        image.save(f'{source_dir}/{title}.webp', format='WEBP')

def __get_summary(title, save_title, redownload):
    if redownload or not os.path.exists(f'{source_dir}/{save_title}.json'):
        data = __make_request(f'/page/summary/{title}')
        __get_image(save_title, thumbnail_override[save_title] if save_title in thumbnail_override else data['thumbnail']['source'])
        with open(f'{source_dir}/{save_title}.json', 'w') as f:
            json.dump(data, f)
        return True
    return False

def __get_page(title, save_title, redownload):
    if redownload or not os.path.exists(f'{source_dir}/{save_title}_page.html'):
        html = __make_request(f'/page/html/{title}', False)
        with open(f'{source_dir}/{save_title}_page.html', 'w') as f:
            f.write(html)
        return True
    return False

def download(pages, redownload = False):
    if not os.path.exists(source_dir):
        os.makedirs(source_dir)
    
    with progress('Downloading Wikipedia entries', len(pages)) as pbar:
        for page in pages:
            # If the page is a list, that means there's fallback options
            pages_to_try = page if isinstance(page, list) else [page]
            i = 0
            for p in pages_to_try:
                try:
                    title = p.replace(' ', '_')
                    did_download = __get_summary(title, pages_to_try[0], redownload)
                    did_download = __get_page(title, pages_to_try[0], redownload) or did_download
                    if did_download:
                        time.sleep(0.1)
                    pbar.update(1)
                    break
                except Exception as e:
                    if i == len(pages_to_try) - 1:
                        print(f'Error downloading {title}')
                        raise e
                    else:
                        print(f'Warning: {title} not found, trying fallback')
                        i += 1