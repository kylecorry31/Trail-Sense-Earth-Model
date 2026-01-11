import csv
import sys
import tqdm

csv.field_size_limit(sys.maxsize)

def get_continent(lat, lon):
    # Antarctica
    if -90 <= lat <= -60:
        return "Antarctica"
    
    # South America
    if -60 < lat <= 7.5 and -180 <= lon <= -30:
        return "South America"
    
    # North America
    if 7.5 < lat <= 90 and -180 <= lon <= -30:
        return "North America"
    
    # Africa
    if -60 < lat <= 35 and -30 < lon <= 35:
        return "Africa"
    
    # Europe
    if 35 < lat <= 90 and -30 < lon <= 45:
        return "Europe"
    
    # Asia
    if (-60 < lat <= 5 and 35 < lon <= 105) or (5 < lat <= 90 and 35 < lon <= 180) or (35 < lat <= 90 and 45 < lon <= 105):
        return "Asia"
    
    # Oceania
    if -60 < lat <= 5 and 105 < lon <= 180:
        return "Australia"
    
    return "Unknown"

CONTINENTS = ["Antarctica", "South America", "North America", "Africa", "Europe", "Asia", "Australia"]


def write_species_counts(all_species):
    with open("output/species_counts.csv", 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species', 'count'] + CONTINENTS
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for species, data in sorted(all_species.items(), key=lambda x: x[1]['count'], reverse=True):
            count = data['count']
            if count < 1000:
                continue
            
            row = data.copy()
            for continent in CONTINENTS:
                row[continent] = int(row[continent] * 100 / count) if count > 0 else 0

            writer.writerow(row)

# Read source/gbif/0003136-260108223611665.csv (stream - it is 64 GB)
i = 0
total = 115893606
with tqdm.tqdm(total=total) as pbar:
    with open("source/gbif/0003136-260108223611665.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        all_species = {}
        for row in reader:

            kingdom = row['kingdom']
            phylum = row['phylum']
            class_ = row['class']
            order = row['order']
            family = row['family']
            genus = row['genus']
            species = row['species']

            full_taxonomy = f"{kingdom};{phylum};{class_};{order};{family};{genus};{species}"

            if full_taxonomy not in all_species:
                all_species[full_taxonomy] = {
                    'kingdom': row['kingdom'],
                    'phylum': row['phylum'],
                    'class': row['class'],
                    'order': row['order'],
                    'family': row['family'],
                    'genus': row['genus'],
                    'species': row['species'],
                    'count': 0,
                    **{c: 0 for c in CONTINENTS}
                }
            
            value = all_species[full_taxonomy]
            try:
                continent = get_continent(float(row['decimalLatitude']), float(row['decimalLongitude']))
                value[continent] += 1
            except (ValueError, TypeError):
                pbar.update(1)
                continue
            value['count'] += 1

            i += 1
            if i % 100000 == 0:
                write_species_counts(all_species)
            pbar.update(1)


write_species_counts(all_species)