import requests
import json
import os
import csv
import time
import math
from .progress import progress

download_dir = 'source/inaturalist'

wikipedia_overrides = {
    'Larus argentatus': 'https://en.wikipedia.org/wiki/European_herring_gull',
    'Troglodytes aedon': 'https://en.wikipedia.org/wiki/Northern_house_wren'
}


def download(number_of_species, redownload = False):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    per_page = 500
    pages = math.ceil(number_of_species / per_page)

    species = []

    with progress('Downloading iNaturalist species counts', total=pages) as pbar:
        for page in range(1, pages + 1):
            if not redownload and os.path.exists(f'{download_dir}/species_counts_{page}.json'):
                with open(f'{download_dir}/species_counts_{page}.json', 'r') as file:
                    data = json.load(file)
            else:
                url = f'https://api.inaturalist.org/v1/observations/species_counts?order_by=count&per_page={per_page}&page={page}'
                response = requests.get(url)
                data = response.json()
                with open(f'{download_dir}/species_counts_{page}.json', 'w') as file:
                    json.dump(data, file)
                time.sleep(0.5)
            
            for record in data['results']:
                scientific_name = record['taxon']['name']
                vernacular_name = record['taxon']['preferred_common_name'] if 'preferred_common_name' in record['taxon'] else ''
                wikipedia_url = record['taxon']['wikipedia_url']
                if scientific_name in wikipedia_overrides:
                    wikipedia_url = wikipedia_overrides[scientific_name]
                
                if wikipedia_url is not None and wikipedia_url != '':
                    species.append({
                        'scientific_name': scientific_name,
                        'vernacular_name': vernacular_name,
                        'wikipedia_url': wikipedia_url
                    })
            pbar.update(1)

    # Write to CSV
    with open(f'{download_dir}/species.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['scientificName', 'vernacularName', 'wikipediaUrl'])
        for data in species:
            writer.writerow([data['scientific_name'], data['vernacular_name'], data['wikipedia_url']])