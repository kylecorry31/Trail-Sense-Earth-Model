from scripts import inaturalist
from scripts import wikipedia
from scripts import progress
from scripts import gemini
import markdownify
import json
import os
import base64
from PIL import Image
import io
import csv
from bs4 import BeautifulSoup
import re
import sqlite3

# INPUT
number_of_species = 500
redownload = False
# Requires google-gemini-api-key.txt, limited to 1500 requests per day
should_summarize = False
regenerate_summaries = False
# The list of scientific names to debug the tag detection
scientific_name_debug_tags = []
image_size = 300
image_quality = 50

######## Program, don't modify ########
output_dir = 'output/species-catalog'
wikipedia_dir = 'source/wikipedia'
species_file = 'source/inaturalist/species.csv'
species_file_scientific_name = 'scientificName'
species_file_common_name = 'vernacularName'
species_file_wikipedia_url = 'wikipediaUrl'
all_tags = {
    # Location
    'Africa': ['Africa'],
    'Antarctica': ['Antarctica'],
    'Asia': ['Asia'],
    'Australia': ['Australia', 'Oceania'],
    'Europe': ['Europe'],
    'North America': ['North America'],
    'South America': ['South America'],
    # Kingdom
    'Plant': ['| Kingdom: | Plantae |'],
    'Animal': ['| Kingdom: | Animalia |'],
    'Fungus': ['| Kingdom: | Fungi |'],
    # Class
    'Bird': ['| Class: | Aves |'],
    'Mammal': ['| Class: | Mammalia |'],
    'Reptile': ['| Class: | Reptilia |'],
    'Amphibian': ['| Class: | Amphibia |'],
    'Fish': ['| Class: | Actinopterygii |', '| Class: | Chondrichthyes |', '| Class: | Sarcopterygii |'],
    'Insect': ['| Class: | Insecta |'],
    'Arachnid': ['| Class: | Arachnida |'],
    'Crustacean': ['| Class: | Crustacea |'],
    'Mollusc': ['| Class: | Mollusca |'],
    # Habitat
    'Forest': ['Forest', 'Woodland', 'Woods'],
    'Desert': ['Desert'],
    'Grassland': ['Grassland', 'Meadow', 'Grassy', 'Steppe', 'Prairie', 'Savanna', 'Lawn', 'Pasture', 'Field'],
    'Wetland': ['Wetland', 'Swamp', 'Marsh', 'Bog', 'Swampy', 'Marshes', 'Fen', 'riverbank', 'riverbed', 'wet soil'],
    'Mountain': ['Mountain', 'Alpine'],
    'Urban': ['Urban', 'City', 'Roadside', 'along road', 'cities'],
    'Marine': ['Marine', 'Ocean', 'Sea', 'Saltwater', 'Salt-water'],
    'Freshwater': ['Freshwater', 'fresh water', 'River', 'Lake', 'Pond', 'Stream'],
    'Cave': ['Cave'],
    'Tundra': ['Tundra', 'Arctic', 'Polar'],
}
# These have incomplete wikipedia entries
species_to_skip = ['Deroceras laeve', 'Solanum dimidiatum',
                   'Oudemansiella furfuracea', 'Stereum lobatum', 'Homo sapiens']
summarize_prompt = """You are a professional content summarizer. Only use information presented in the text to summarize. If something isn't mentioned, leave it out. Write a description of the species. It should include some key features to help identify it, whether it is edible (but only if explicitely mentioned), and where it can be found (habitat and geographic location). If the common name is provided, use that instead of the scientific name. Your entire summarization MUST have at most 4 sentences.

TEXT TO SUMMARIZE:
<>

SUMMARY:"""
license_overrides = {
    'Trifolium repens': {
        'user': 'Vinayaraj',
        'license': 'CC BY-SA 4.0',
    },
    'Asclepias syriaca': {
        'user': 'Amos Oliver Doyle',
        'license': 'CC BY-SA 4.0',
    },
    'Urtica dioica': {
        'user': 'Skalle-Per Hedenhös',
        'license': 'CC BY-SA 4.0',
    },
    'Bufo bufo': {
        'user': 'Tythatguy1312',
        'license': 'CC BY-SA 4.0',
    },
    'Carnegiea gigantea': {
        'user': 'WClarke',
        'license': 'CC BY-SA 3.0',
    },
    'Fagus sylvatica': {
        'user': 'GooseCanada',
        'license': 'CC BY-SA 4.0',
    }
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


def summarize(id, text):
    prompt = summarize_prompt.replace("<>", text)
    summarized = gemini.process(id, prompt, regenerate_summaries)
    return summarized


def regex_word(word):
    return r'[^\w"-]' + word + r'[^\w"-]'


def contains_word(text, word, should_print=False):
    escaped = re.escape(word) + r's?'
    # Near isn't a negation in all cases, maybe pass in a list of additional negations for a single word
    negations_before = ['except', 'not', 'near', 'apart from']
    negations_after = []
    false_positivies = ['river basin', 'rocky mountains', 'seasonal pasture myopathy',
                        'fields of', 'field of', 'the field', 'field studies', 'field study', 'field research', 'field testing', 'field test', 'field guide', 'field work']
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s|\n', text)
    matches = list(filter(lambda x: x is not None, [
        sentence for sentence in sentences
        if re.search(regex_word(escaped), sentence) is not None
        and not any(re.search(regex_word(re.escape(false_positive) + r's?'), sentence) for false_positive in false_positivies)
        and not any(re.search(regex_word(re.escape(negation)) + r'[^\.\n]*' + regex_word(escaped), sentence) for negation in negations_before)
        and not any(re.search(regex_word(escaped) + r'?[^\.\n]*' + regex_word(re.escape(negation)), sentence) for negation in negations_after)
    ]))
    has_keyword = any(matches)
    if not has_keyword:
        return False

    if should_print:
        print("KEYWORD:", word)
        for match in matches:
            print("MATCH:", match)
            print()

    return True


if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the species from iNaturalist
inaturalist.download(number_of_species, redownload)
species_to_lookup = []
with open(species_file, 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if len(scientific_name_debug_tags) == 0 or row[species_file_scientific_name] in scientific_name_debug_tags:
            species_to_lookup.append((row[species_file_scientific_name],
                                      row[species_file_common_name], row[species_file_wikipedia_url]))

species_to_lookup = [
    species for species in species_to_lookup if species[0] not in species_to_skip]

# Lookup the species on Wikipedia
wikipedia.download([[scientific_name.replace(' ', '_'), wikipediaUrl.split('/')[-1], common_name]
                   for (scientific_name, common_name, wikipediaUrl) in species_to_lookup], redownload)

# Delete existing species catalog entries
for file in os.listdir(output_dir):
    os.remove(f'{output_dir}/{file}')

# Create a sqlite database
if os.path.exists('output/species-catalog.db'):
    os.remove('output/species-catalog.db')
conn = sqlite3.connect('output/species-catalog.db')
c = conn.cursor()
c.execute(
    'CREATE TABLE IF NOT EXISTS species (scientific_name TEXT PRIMARY KEY, name TEXT, images BLOB, notes TEXT, tags TEXT)')

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

            with open(f'{wikipedia_dir}/{title}_image_metadata.json', 'r') as f:
                image_metadata = json.load(f)

            page = get_sections(html)

            with open(f'{wikipedia_dir}/{title}.webp', 'rb') as f:
                image_bytes = f.read()
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((image_size, image_size))
            buffer = io.BytesIO()
            image.save(buffer, format='WEBP', quality=image_quality)
            image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            name = common_name if common_name != '' and common_name != scientific_name else summary[
                'title']
            url = summary['content_urls']['mobile']['page']
            uses = page.get('Uses', '')
            distribution = page.get('Distribution', page.get(
                'Range', page.get('Distribution and habitat', '')))

            # Image license info
            page_id = next(iter(image_metadata['query']['pages']))
            image_info = image_metadata['query']['pages'][page_id]['imageinfo'][
                0] if 'imageinfo' in image_metadata['query']['pages'][page_id] else None
            user = image_info['user'] if image_info is not None else ''
            license = image_info['extmetadata']['LicenseShortName']['value'] if image_info is not None else ''

            if scientific_name in license_overrides:
                user = license_overrides[scientific_name]['user']
                license = license_overrides[scientific_name]['license']

            if license == '':
                print(f'No license found for {scientific_name}')

            lower_page = page['full'].lower()
            tags = []
            for tag in all_tags:
                if any([contains_word(lower_page, t.lower(), scientific_name in scientific_name_debug_tags) for t in all_tags[tag]]):
                    tags.append(tag)

            description = page.get('Description', '')

            notes = []
            notes.append(page.get("Abstract", "").strip())

            if should_summarize:
                notes.append(description)

                if uses != '':
                    notes.append(f'Uses\n\n{uses}'.strip())

                if distribution != '':
                    notes.append(f'Distribution\n\n{distribution}'.strip())
                summarized = summarize(scientific_name, '\n\n'.join(notes))
                notes = []
                notes.append(summarized)

            notes.append(f'The text is sourced from Wikipedia ({
                         url}), licensed under CC BY-SA 4.0.')
            notes.append(f'The image is sourced from Wikipedia. Uploaded by {
                         user}, licensed under {license}.')

            data = {
                'name': name.title() if name.lower() != scientific_name.lower() else name.capitalize(),
                'images': [image],
                'notes': '\n\n'.join(notes),
                'tags': tags
            }

            with open(f'{output_dir}/{scientific_name}.json', 'w') as f:
                json.dump(data, f)

            # Load into a sqlite database
            image_bytes = base64.b64decode(image)

            c.execute('INSERT INTO species VALUES (?, ?, ?, ?, ?)',
                      (scientific_name, name, image_bytes,
                       data['notes'], json.dumps(data['tags']))
                      )

            pbar.update(1)
        except Exception as e:
            print(f'Error processing {scientific_name}')
            raise e
conn.commit()
conn.close()
