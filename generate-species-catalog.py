from scripts import wikipedia
from scripts import progress
from scripts.species_catalog.openai_summarizer import OpenAISummarizer
from scripts.species_catalog.gemini_summarizer import GeminiSummarizer
from scripts.species_catalog.parser_summarizer import ParserSummarizer
import markdownify
import json
import os
import base64
from PIL import Image
import io
from bs4 import BeautifulSoup
import zipfile

# INPUT
pages = [
    'Squirrel',
    'Deer',
    'Pronghorn',
    'Muridae',
    'Racoon',
    'Opposum',
    'Frog',
    'Beaver',
    'Meleagris',
    'Bear',
    'Leporidae',
    'Grouse',
    'Quail',
    'Pheasant',
    'Columbidae',
    'Anatidae',
    'Rallidae',
    'Snipe',
    'Woodcock',
    'Passerellidae',
    'Corvid',
    'Suina',
    'Lepomis',
    'Micropterus',
    'Pomoxis',
    'Cyprinus',
    'Siluriformes',
    'Salmonidae',
    'Trout',
    'Perch',
    'Lepisosteidae',
    'Bowfin',
    'Canis',
    'Toad',
    'Snake',
    'Turtle',
    'Lizard',
    'Crocodilian',
    'Chelydridae',
    'Big cat',
    'Chiroptera',
    'Lynx',
    'Mustelidae',
    'Skunk',
    'Viverridae',
    'Hyena',
    'Pinniped',
    'Porcupine',
    'Eulipotyphla',
    'Armadillo',
    'Caprinae',
    'Caviidae',
    'Tinamidae',
    'Dasyproctidae',
    'Hippopotamidae',
    'Camelidae',
    'Tapir',
    'Partridge',
    'Guineafowl',
    'Gallini_(bird)',
    'Pedetidae',
    'Antelope',
    'Bovina_(subtribe)',
    'Equidae',
    'Macropodidae',

    # Rocks
    'Chert',
    'Granite',
    'Basalt',
    'Obsidian',
]

redownload = False
should_summarize = False
# Requires google-gemini-api-key.txt, limited to 1500 free requests per day
# summary_source = 'gemini'
# Requires openai-api-key.txt, costs money
summary_source = 'openai'
regenerate_summaries = False
names_to_debug = []
image_size = 250
max_image_quality = 80
min_image_quality = 30
max_image_size_kb = 5
license_overrides = {}

######## Program, don't modify ########
output_dir = 'output/species-catalog'
wikipedia_dir = 'source/wikipedia'
tag_to_id = {
    'Africa': 1,
    'Antarctica': 2,
    'Asia': 3,
    'Australia': 4,
    'Europe': 5,
    'North America': 6,
    'South America': 7,
    'Plant': 8,
    'Animal': 9,
    'Fungus': 10,
    'Bird': 11,
    'Mammal': 12,
    'Reptile': 13,
    'Amphibian': 14,
    'Fish': 15,
    'Insect': 16,
    'Arachnid': 17,
    'Crustacean': 18,
    'Mollusk': 19,
    'Forest': 20,
    'Desert': 21,
    'Grassland': 22,
    'Wetland': 23,
    'Mountain': 24,
    'Urban': 25,
    'Marine': 26,
    'Freshwater': 27,
    'Cave': 28,
    'Tundra': 29,
}

def get_sections(html):

    # Preprocess the html by removing all text after the reference sections
    reference_sections = [
        'References',
        'Citations',
        'External_links',
        'See_also',
    ]

    for section in reference_sections:
        html = html.split(f'<h2 id="{section}">')[0]

    soup = BeautifulSoup(html, 'html.parser')
    elements_to_delete = [
        'title',
        'meta',
        'link',
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

    for tag in soup.find_all(None, {'style': 'display:none'}):
        tag.decompose()

    full_html = str(soup)

    tables = [
        'table',
        'tbody',
        'tr',
        'td',
        'th',
        'thead',
    ]
    for element in tables:
        for tag in soup.find_all(element):
            tag.decompose()

    html = str(soup)
    markdown = markdownify.markdownify(
        html, strip=['a', 'img', 'b', 'i'], heading_style='ATX')
    # A section is pair of header followed by the content until the next header
    sections = {}
    lines = markdown.split('\n')
    current_section = 'Abstract'
    sections[current_section] = []
    for line in lines:
        if line.startswith('## '):
            if current_section is not None:
                sections[current_section] = '\n'.join(
                    sections[current_section]).strip()
            current_section = line.replace('## ', '').strip()
            sections[current_section] = []
        elif current_section is not None:
            sections[current_section].append(line)
    if current_section is not None:
        sections[current_section] = '\n'.join(
            sections[current_section]).strip()
    html_before_references = full_html
    sections['full'] = markdownify.markdownify(html_before_references, strip=[
                                               'a', 'img', 'b', 'i'], heading_style='ATX')
    return sections


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

licenses = set()

# Lookup the species on Wikipedia
wikipedia.download(pages, redownload)

# Delete existing species catalog entries
for file in os.listdir(output_dir):
    os.remove(f'{output_dir}/{file}')

# Generate species catalog entries
with progress.progress('Processing species catalog', len(pages)) as pbar:
    for page in pages:
        try:
            title = page
            with open(f'{wikipedia_dir}/{title}.json', 'r') as f:
                summary = json.load(f)

            with open(f'{wikipedia_dir}/{title}_page.html', 'r') as f:
                html = f.read()

            with open(f'{wikipedia_dir}/{title}_image_metadata.json', 'r') as f:
                image_metadata = json.load(f)

            sections = get_sections(html)

            with open(f'{wikipedia_dir}/{title}.webp', 'rb') as f:
                image_bytes = f.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((image_size, image_size))
            buffer = io.BytesIO()
            image_quality = max_image_quality
            image.save(buffer, format='WEBP', quality=image_quality)
            max_image_size_bytes = max_image_size_kb * 1024
            while image_quality > min_image_quality and buffer.getbuffer().nbytes > max_image_size_bytes:
                buffer = io.BytesIO()
                image_quality -= 10
                image.save(buffer, format='WEBP', quality=image_quality)
            image.save(f'{output_dir}/{title}.webp', format='WEBP', quality=image_quality)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            name = summary['title']
            url = summary['content_urls']['mobile']['page']
            sections['extract'] = summary['extract']

            # Image license info
            page_id = next(iter(image_metadata['query']['pages']))
            image_info = image_metadata['query']['pages'][page_id]['imageinfo'][
                0] if 'imageinfo' in image_metadata['query']['pages'][page_id] else None
            user = image_info['user'] if image_info is not None else ''
            license = image_info['extmetadata']['LicenseShortName']['value'] if image_info is not None else ''

            if name in license_overrides:
                user = license_overrides[name]['user']
                license = license_overrides[name]['license']

            licenses.add(license)

            if license == '':
                print(f'No license found for {name}')

            summarizer = ParserSummarizer(names_to_debug)
            if should_summarize and summary_source == 'gemini':
                summarizer = GeminiSummarizer(
                    regenerate_summaries, names_to_debug)
            elif should_summarize and summary_source == 'openai':
                summarizer = OpenAISummarizer(regenerate_summaries)

            notes = []
            summarized = summarizer.summarize(name, name, sections)
            name = summarized['name']
            tags = summarized['tags']
            tags = [tag_to_id[tag] for tag in tags if tag in tag_to_id]

            notes.append(summarized['notes'])
            notes.append(f'Text derived from {url} (CC BY-SA 4.0)')
            notes.append(f'Image by {user} ({license})')

            data = {
                'name': name.title().replace("'S", "'s"),
                'notes': '\n\n'.join(notes),
                'images': [image],
                'tags': tags,
            }

            with open(f'{output_dir}/{title}.json', 'w') as f:
                json.dump(data, f)            

            pbar.update(1)
        except Exception as e:
            print(f'Error processing {title}')
            raise e

# Write all json files into a zip file
with zipfile.ZipFile(f'{output_dir}.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for file in os.listdir(output_dir):
        if file.endswith('.json'):
            z.write(f'{output_dir}/{file}', file)

print('Size:', os.path.getsize(f'{output_dir}.zip') / 1024, 'KB')

print('Licenses:', licenses)
