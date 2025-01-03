from scripts import inaturalist
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
import csv
from bs4 import BeautifulSoup
import zipfile

# INPUT
number_of_species = 2000
redownload = False
should_summarize = True
# Requires google-gemini-api-key.txt, limited to 1500 free requests per day
# summary_source = 'gemini'
# Requires openai-api-key.txt, costs money
summary_source = 'openai'
regenerate_summaries = False
# The list of scientific names to debug the tag detection
scientific_name_debug_tags = []
image_size = 300
image_quality = 50
condensed_image_size = 300
condensed_image_quality = 50
condensed_catalog_counts = {
    'Plant': 150,
    'Mammal': 40,
    'Bird': 30,
    'Reptile': 30,
    'Amphibian': 20,
    'Fish': 20,
    'Insect': 40,
    'Arachnid': 20,
    'Mollusk': 10,
    'Crustacean': 10,
    'Fungus': 50,
}

######## Program, don't modify ########
output_dir = 'output/species-catalog'
wikipedia_dir = 'source/wikipedia'
species_file = 'source/inaturalist/species.csv'
species_file_scientific_name = 'scientificName'
species_file_common_name = 'vernacularName'
species_file_wikipedia_url = 'wikipediaUrl'
# These have incomplete wikipedia entries
species_to_skip = ['Deroceras laeve', 'Solanum dimidiatum',
                   'Oudemansiella furfuracea', 'Stereum lobatum', 'Homo sapiens']


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
    },
    'Persicaria virginiana': {
        'user': 'weeg',
        'license': 'CC0'
    },
    'Echinocereus engelmannii': {
        'user': 'Clayton Esterson',
        'license': 'Public Domain'
    },
    'Rubus allegheniensis': {
        'user': 'USDA-NRCS PLANTS Database',
        'license': 'PD-US'
    },
    'Carya ovata': {
        'user': 'Famartin',
        'license': 'CC BY-SA 4.0'
    },
    'Melanerpes aurifrons': {
        'user': 'Charles J. Sharp',
        'license': 'CC BY-SA 4.0'
    },
    'Arum italicum': {
        'user': 'Consultaplantas',
        'license': 'CC BY-SA 4.0'
    },
    'Manduca sexta': {
        'user': 'Wesxdz',
        'license': 'CC0'
    },
    'Betula nigra': {
        'user': 'Greg Hume',
        'license': 'CC BY-SA 4.0'
    },
    'Eriobotrya japonica': {
        'user': 'Aftabbanoori',
        'license': 'CC BY-SA 3.0'
    },
    'Quercus phellos': {
        'user': 'Freekhou5',
        'license': 'CC BY-SA 4.0'
    },
    'Campanula persicifolia': {
        'user': 'Skalle-Per Hedenhös',
        'license': 'CC BY-SA 4.0'
    },
    'Heptapleurum arboricola': {
        'user': 'JMK',
        'license': 'CC BY-SA 3.0'
    }

}

resolved = []


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

# Load the species from iNaturalist
inaturalist.download(number_of_species, redownload)
count = 0
species_to_lookup = []
with open(species_file, 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        if len(scientific_name_debug_tags) == 0 or row[species_file_scientific_name] in scientific_name_debug_tags:
            species_to_lookup.append((row[species_file_scientific_name],
                                      row[species_file_common_name], row[species_file_wikipedia_url]))
original_len = len(species_to_lookup)
species_to_lookup = [
    species for species in species_to_lookup if species[0] not in species_to_skip]
count = original_len - len(species_to_lookup)

# Lookup the species on Wikipedia
wikipedia.download([[scientific_name.replace(' ', '_'), wikipediaUrl.split('/')[-1], common_name]
                   for (scientific_name, common_name, wikipediaUrl) in species_to_lookup], redownload)

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

            # Image license info
            page_id = next(iter(image_metadata['query']['pages']))
            image_info = image_metadata['query']['pages'][page_id]['imageinfo'][
                0] if 'imageinfo' in image_metadata['query']['pages'][page_id] else None
            user = image_info['user'] if image_info is not None else ''
            license = image_info['extmetadata']['LicenseShortName']['value'] if image_info is not None else ''

            if scientific_name in license_overrides:
                user = license_overrides[scientific_name]['user']
                license = license_overrides[scientific_name]['license']

            licenses.add(license)

            if license == '':
                print(f'No license found for {scientific_name}')

            summarizer = ParserSummarizer(scientific_name_debug_tags)
            if should_summarize and summary_source == 'gemini':
                summarizer = GeminiSummarizer(
                    regenerate_summaries, scientific_name_debug_tags)
            elif should_summarize and summary_source == 'openai':
                summarizer = OpenAISummarizer(regenerate_summaries)

            notes = []
            summarized = summarizer.summarize(scientific_name, name, page)
            name = summarized['name']
            tags = summarized['tags']

            notes.append(summarized['notes'])
            notes.append(f'Text derived from {url} (CC BY-SA 4.0)')
            notes.append(f'Image by {user} ({license})')

            # Add to resolved before minifying the tags
            resolved.append([scientific_name, tags])

            tags = [tag_to_id[tag] for tag in tags if tag in tag_to_id]

            data = {
                'name': name.title() if name.lower() != scientific_name.lower() else name.capitalize(),
                'images': [image],
                'notes': '\n\n'.join(notes),
                'tags': tags,
            }

            with open(f'{output_dir}/{scientific_name}.json', 'w') as f:
                json.dump(data, f)

            count += 1
            # If the count is divisible by 500, create a zip file of all the .json files
            if count % 500 == 0:
                with zipfile.ZipFile(f'{output_dir}/species-catalog-top-{count}.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
                    for file in os.listdir(output_dir):
                        if file.endswith('.json'):
                            z.write(f'{output_dir}/{file}', file)

            pbar.update(1)
        except Exception as e:
            print(f'Error processing {scientific_name}')
            raise e

# Create a condensed species catalog
species_to_export = {
    'Plant': [],
    'Mammal': [],
    'Bird': [],
    'Reptile': [],
    'Amphibian': [],
    'Fish': [],
    'Insect': [],
    'Arachnid': [],
    'Mollusk': [],
    'Crustacean': [],
    'Fungus': [],
}

for species in resolved:
    scientific_name, tags = species
    for tag in tags:
        if tag in species_to_export and len(species_to_export[tag]) < condensed_catalog_counts[tag]:
            species_to_export[tag].append(scientific_name)
            break

# Generate a zip file of all the species to export
with zipfile.ZipFile(f'{output_dir}/species-catalog.zip', 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for tag in species_to_export:
        for species in species_to_export[tag]:
            if condensed_image_quality != image_quality or condensed_image_size != image_size:
                with open(f'{output_dir}/{species}.json', 'r') as f:
                    data = json.load(f)
                image = data['images'][0]
                image = base64.b64decode(image)
                image = Image.open(io.BytesIO(image))
                image.thumbnail((condensed_image_size, condensed_image_size))
                buffer = io.BytesIO()
                image.save(buffer, format='WEBP', quality=condensed_image_quality)
                image = base64.b64encode(buffer.getvalue()).decode('utf-8')
                data['images'] = [image]
                with open(f'{output_dir}/{species}.json', 'w') as f:
                    json.dump(data, f)
            z.write(f'{output_dir}/{species}.json', f'{species}.json')

print('Licenses:', licenses)
