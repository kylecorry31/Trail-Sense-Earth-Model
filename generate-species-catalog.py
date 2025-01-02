from scripts import inaturalist
from scripts import wikipedia
from scripts import progress
from scripts import gemini
import markdownify
import json
import re
import os
import base64
from PIL import Image
import io
import csv
import time
from bs4 import BeautifulSoup

# INPUT
number_of_species = 500
redownload = False
should_summarize = False # Requires google-gemini-api-key.txt, limited to 1500 requests per day

######## Program, don't modify ########
output_dir = 'output/species-catalog'
wikipedia_dir = 'source/wikipedia'
species_file = 'source/inaturalist/species.csv'
species_file_scientific_name = 'scientificName'
species_file_common_name = 'vernacularName'
species_file_wikipedia_url = 'wikipediaUrl'
all_continents = ['Africa', 'Antarctica', 'Asia', 'Australia', 'Europe', 'North America', 'South America']
kingdoms = ['Plantae', 'Animalia', 'Fungi']
classes = {
    'Bird': ['Aves'],
    'Mammal': ['Mammalia'],
    'Reptile': ['Reptilia'],
    'Amphibian': ['Amphibia'],
    'Fish': ['Actinopterygii', 'Chondrichthyes', 'Sarcopterygii'],
    'Insect': ['Insecta'],
    'Arachnid': ['Arachnida'],
    'Crustacean': ['Crustacea'],
    'Mollusc': ['Mollusca'],
}
# These have incomplete wikipedia entries
species_to_skip = ['Deroceras laeve', 'Solanum dimidiatum', 'Oudemansiella furfuracea', 'Stereum lobatum']
summarize_prompt = """You are a professional content summarizer. Only use information presented in the text to summarize. If something isn't mentioned, leave it out. Write a description of the species. It should include some key features to help identify it, whether it is edible (but only if explicitely mentioned), and where it can be found (habitat and geographic location). If the common name is provided, use that instead of the scientific name. Your entire summarization MUST have at most 4 sentences.

TEXT TO SUMMARIZE:
<>

SUMMARY:"""

def get_sections(html):
    original_html = html
    soup = BeautifulSoup(html, 'html.parser')
    elements_to_delete = [
        'title',
        'meta',
        'link',
        'table',
        'tbody',
        'tr',
        'td',
        'th',
        'thead',
        'figure',
        'sup',
    ]

    for element in elements_to_delete:
        for tag in soup.find_all(element):
            tag.decompose()
    
    for tag in soup.find_all('div', {'role': 'note'}):
        tag.decompose()
    
    for tag in soup.find_all('ul', {'class': 'gallery'}):
        tag.decompose()
    
    for tag in soup.find_all('span', {'class': 'rt-commentedText'}):
        tag.decompose()
    
    for tag in soup.find_all(None, {'style': 'display:none'}):
        tag.decompose()

    html = str(soup)
    html = html.replace('()', '')
    markdown = markdownify.markdownify(html, strip=['a', 'img', 'b', 'i'], heading_style='ATX')
    markdown = markdown.replace('\xa0', ' ').replace('\u2013', '-').replace('\u00a0', ' ').replace('\u2044', '/')
    # A section is pair of header followed by the content until the next header
    sections = {}
    lines = markdown.split('\n')
    current_section = 'Abstract'
    sections[current_section] = []
    for line in lines:
        if line.startswith('## '):
            if current_section is not None:
                sections[current_section] = '\n'.join(sections[current_section]).strip()
            current_section = line.replace('## ', '').strip()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)
    if current_section is not None:
        sections[current_section] = '\n'.join(sections[current_section]).strip()
    sections['full'] = original_html
    return sections

def summarize(text):
    prompt = summarize_prompt.replace("<>", text)
    summarized = gemini.process(prompt)
    # Limit to 15 requests per minute
    time.sleep(4)
    return summarized

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the species from iNaturalist
inaturalist.download(number_of_species, redownload)
species_to_lookup = []
with open(species_file, 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        species_to_lookup.append((row[species_file_scientific_name], row[species_file_common_name], row[species_file_wikipedia_url]))

species_to_lookup = [species for species in species_to_lookup if species[0] not in species_to_skip]

# Lookup the species on Wikipedia
wikipedia.download([[scientific_name.replace(' ', '_'), wikipediaUrl.split('/')[-1], common_name] for (scientific_name, common_name, wikipediaUrl) in species_to_lookup], redownload)

# Delete existing species catalog entries
for file in os.listdir(output_dir):
    os.remove(f'{output_dir}/{file}')

# Generate species catalog entries
with progress.progress('Processing species catalog', len(species_to_lookup)) as pbar:
    for species in species_to_lookup:
        try:
            (scientific_name, common_name, wikipediaUrl) = species
            title = scientific_name.replace(' ', '_')
            with open(f'{wikipedia_dir}/{title}.json', 'r') as f:
                summary = json.load(f)
            
            with open(f'{wikipedia_dir}/{title}_page.html', 'r') as f:
                html = f.read()
            
            page = get_sections(html)

            with open(f'{wikipedia_dir}/{title}.webp', 'rb') as f:
                image_bytes = f.read()
            image = Image.open(io.BytesIO(image_bytes))
            image_size = 300
            image.thumbnail((image_size, image_size))
            buffer = io.BytesIO()
            image.save(buffer, format='WEBP', quality=75)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            name = common_name if common_name != '' and common_name != scientific_name else summary['title']
            url = summary['content_urls']['mobile']['page']
            uses = page.get('Uses', '')
            distribution = page.get('Distribution', page.get('Range', page.get('Distribution and habitat', '')))

            kingdom = None
            for k in kingdoms:
                if k in page['full']:
                    kingdom = k
                    break

            _class = None
            for c in classes:
                if any([cl in page['full'] for cl in classes[c]]):
                    _class = c
                    break
            
            continents = [continent for continent in all_continents if continent in page['full']]

            description = page.get('Description', '')

            notes = []
            notes.append(page.get("Abstract", "").strip())

            if should_summarize:
                notes.append(description)

                if uses != '':
                    notes.append(f'Uses\n\n{uses}'.strip())

                if distribution != '':
                    notes.append(f'Distribution\n\n{distribution}'.strip())
                summarized = summarize('\n\n'.join(notes))
                notes = []
                notes.append(summarized)

            notes.append('Image and content are from Wikipedia')
            notes.append(url)

            data = {
                'name': name.title() if name.lower() != scientific_name.lower() else name.capitalize(),
                'images': [image],
                'notes': '\n\n'.join(notes),
                'category': kingdom,
                'subcategory': _class,
                'continents': continents
            }

            with open(f'{output_dir}/{scientific_name}.json', 'w') as f:
                json.dump(data, f)

            pbar.update(1)
        except Exception as e:
            print(f'Error processing {scientific_name}')
            raise e