from scripts import simbad
import numpy as np

stars = [
    'Sirius',
    'Canopus',
    'Rigil Kentaurus',
    'Arcturus',
    'Vega',
    'Rigel',
    'Procyon',
    'Achernar',
    'Betelgeuse',
    'Hadar',
    'Altair',
    'Acrux',
    'Aldebaran',
    'Antares',
    'Spica',
    'Pollux',
    'Fomalhaut',
    'Deneb',
    'Mimosa',
    'Regulus',
    'Adhara',
    'Castor',
    'Shaula',
    'Gacrux',
    'Bellatrix',
    'Elnath',
    'Miaplacidus',
    'Alnilam',
    'Alnair',
    'Alnitak',
    'Alioth',
    'Dubhe',
    'Mirfak',
    'Wezen',
    'Regor',
    'Sargas',
    'Kaus Australis',
    'Avior',
    'Alkaid',
    'Menkalinan',
    'Atria',
    'Alhena',
    'Peacock',
    'Alsephina',
    'Mirzam',
    'Polaris',
    'Alphard',
    'Hamal',
    'Diphda',
    'Alpheratz',
    'Ankaa',
    'Schedar',
    'Acamar',
    'Menkar',
    'Capella',
    'Suhail',
    'Denebola',
    'Gienah',
    'Menkent',
    'Zubenelgenubi',
    'Kochab',
    'Alphecca',
    'Sabik',
    'Rasalhague',
    'Eltanin',
    'Nunki',
    'Enif',
    'Markab',
    'Merak',
    'Phecda',
    'Megrez',
    'Mizar',
    'Imai',
    'Ginan',
    'Saiph',
    'Meissa',
    'Mintaka',
    'Mirach',
    'Algieba',
    'Algol',
    'Tiaki',
    'Muhlifain',
    'Aspidiske',
    'Sadr',
    'Naos',
    'Almach',
    'Caph',
    'Uridim',
    'Epsilon Centauri',
    'Dschubba',
    'Larawag',
    'Eta Centauri',
    'Girtab',
    'Scheat',
    'Aludra',
    'Alderamin',
    # 'Markeb',
    'Gamma Cassiopeiae',
    'Aljanah',
    'Acrab',
    'Ruchbah',
    'Segin',
    'Izar'
]

for star in stars:
    id, ra, dec, v_mag, pm_ra, pm_dec, color_index = simbad.get_star_details(star)
    print(f"Star(\"{star}\", EquatorialCoordinate({dec}, {ra}), {v_mag}f, ProperMotion({pm_dec}, {pm_ra}), {(str(color_index) + 'f') if not np.isnan(color_index) else 'null'}),")  

# stars = simbad.get_bright_objects()
# stars = [star for star in stars if star[0].startswith('*')]

# to_remove = []
# for star in stars:
#     id = star[0]
#     last = id.split(' ')[-1]
#     if len(last) == 1 and last.isalpha():
#         # See if there's a star with the same base id
#         base_id = id[:-1].strip()
#         if any(s[0] == base_id for s in stars):
#             to_remove.append(star)

# for star in to_remove:
#     stars.remove(star)

# # Sort stars by the second word in the ID and then by the first word
# stars.sort(key=lambda x: x[0][1:].strip().split(' ')[1].lower() + " " + x[0][1:].strip().split(' ')[0].lower())

# for star in stars:
#     id = star[0][1:].strip()
#     names = f'"{",".join([name.title() for name in star[1]])}"'
#     ra = star[2]
#     dec = star[3]
#     v_mag = star[4]
#     pm_ra = star[5]
#     pm_dec = star[6]
#     color_index = star[7]
#     print(f"Star(\"{id}\", {names}, EquatorialCoordinate({dec}, {ra}), {v_mag}f, ProperMotion({pm_dec}, {pm_ra}), {(str(color_index) + 'f') if not np.isnan(color_index) else 'null'}),")