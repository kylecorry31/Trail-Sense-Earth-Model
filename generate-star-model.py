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
    'Gamma Centauri',
    'Aspidiske',
    'Sadr',
    'Naos',
    'Almach',
    'Caph',
    'Alpha Lupi',
    'Epsilon Centauri',
    'Dschubba',
    'Larawag',
    'Eta Centauri',
    'Kappa Scorpii',
    'Scheat',
    'Aludra',
    'Alderamin',
    'Markeb',
    'Gamma Cassiopeiae',
    'Aljanah',
    'Acrab',
    'Ruchbah',
    'Segin'
]

for star in stars:
    ra, dec, v_mag, pm_ra, pm_dec, color_index = simbad.get_star_details(star)
    print(f"{star.replace(' ', '')}(EquatorialCoordinate({dec}, {ra}), {v_mag}f, ProperMotion({pm_dec}, {pm_ra}), {(str(color_index) + 'f') if not np.isnan(color_index) else 'null'}),")  