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
    'Asparagus_officinalis': 'https://upload.wikimedia.org/wikipedia/commons/0/0c/Illustration_Asparagus_officinalis0b.jpg',
    'Corvid': 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Corvus_corone_-near_Canford_Cliffs%2C_Poole%2C_England-8.jpg',
    'Big cat': 'https://upload.wikimedia.org/wikipedia/commons/c/cd/4panthera3.0.png',
    'Betulaceae': 'https://upload.wikimedia.org/wikipedia/commons/6/60/Corylus_avellana.jpg',
    'Acarina': 'https://upload.wikimedia.org/wikipedia/commons/2/29/Amblyomma_americanum_tick.jpg',
    'Carnivora': 'https://upload.wikimedia.org/wikipedia/commons/4/43/Carnivora_portraits.jpg',
    'Ericaceae': 'https://upload.wikimedia.org/wikipedia/commons/2/28/Maturing_blueberry.jpg',
    'Fagaceae': 'https://upload.wikimedia.org/wikipedia/commons/a/af/Quercus_robur.jpg',
    'Polyporales': 'https://upload.wikimedia.org/wikipedia/commons/7/7c/2007-06-27_Laetiporus_sulphureus_crop.jpg',
    'Pleuronectiformes': 'https://upload.wikimedia.org/wikipedia/commons/2/2b/Pseudopleuronectes_americanus.jpg',
    'Plantaginaceae': 'https://upload.wikimedia.org/wikipedia/commons/6/6e/Plantago_major.jpg',
    'Fern': 'https://upload.wikimedia.org/wikipedia/commons/4/47/The_ferns_of_Great_Britain%2C_and_their_allies_the_club-mosses%2C_pepperworts%2C_and_horsetails_%28Pl._2%29_%288515393495%29.jpg',
    'Cucurbitaceae': 'https://upload.wikimedia.org/wikipedia/commons/f/fc/Flower_of_Lagenaria_captured_at_night.jpg',
    'Anseriformes': 'https://upload.wikimedia.org/wikipedia/commons/3/33/%D7%91%D7%A8%D7%95%D7%95%D7%96%D7%99%D7%99%D7%9D-01.jpg',
    'Melanerpes_aurifrons': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Golden-fronted_%28Velasquez%27s%29_woodpecker_%28Melanerpes_aurifrons%29_male_Copan.jpg/320px-Golden-fronted_%28Velasquez%27s%29_woodpecker_%28Melanerpes_aurifrons%29_male_Copan.jpg',
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
    downloaded_image = False
    if redownload or not os.path.exists(f'{source_dir}/{save_title}.json'):
        data = __make_request(f'/page/summary/{title}')
        __get_image(save_title, thumbnail_override[save_title] if save_title in thumbnail_override else data['thumbnail']['source'])
        with open(f'{source_dir}/{save_title}.json', 'w') as f:
            json.dump(data, f)
        downloaded_image = True
    
    if redownload or not os.path.exists(f'{source_dir}/{save_title}_image_metadata.json'):
        # Load image path
        with open(f'{source_dir}/{save_title}.json', 'r') as f:
            data = json.load(f)
        orignal_image_url = thumbnail_override[save_title] if save_title in thumbnail_override else data['originalimage']['source']
        url = f'https://commons.wikimedia.org/w/api.php?action=query&titles=File:{orignal_image_url.split("/")[-1]}&prop=imageinfo&iiprop=user|extmetadata&format=json'
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f'Error: {response.status_code}, {response.text}')
        with open(f'{source_dir}/{save_title}_image_metadata.json', 'w') as f:
            f.write(response.text)
        return True
    return downloaded_image

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