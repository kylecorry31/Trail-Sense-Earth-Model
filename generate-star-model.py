from scripts import simbad
import numpy as np

constellation_abbreviation_to_name = {
    "And": "Andromedae",
    "Ant": "Antliae",
    "Aps": "Apodis",
    "Aqr": "Aquarii",
    "Aql": "Aquilae",
    "Ara": "Arae",
    "Ari": "Arietis",
    "Aur": "Aurigae",
    "Boo": "Boötis",
    "Cae": "Caeli",
    "Cam": "Camelopardalis",
    "Cnc": "Cancri",
    "CVn": "Canum Venaticorum",
    "CMa": "Canis Majoris",
    "CMi": "Canis Minoris",
    "Cap": "Capricorni",
    "Car": "Carinae",
    "Cas": "Cassiopeiae",
    "Cen": "Centauri",
    "Cep": "Cephei",
    "Cet": "Ceti",
    "Cha": "Chamaeleontis",
    "Cir": "Circini",
    "Col": "Columbae",
    "Com": "Comae Berenices",
    "CrA": "Coronae Australis",
    "CrB": "Coronae Borealis",
    "Crv": "Corvi",
    "Crt": "Crateris",
    "Cru": "Crux",
    "Cyg": "Cygni",
    "Del": "Delphini",
    "Dor": "Doradus",
    "Dra": "Draconis",
    "Equ": "Equulei",
    "Eri": "Eridani",
    "For": "Fornacis",
    "Gem": "Geminorum",
    "Gru": "Gruis",
    "Her": "Herculis",
    "Hor": "Horologii",
    "Hya": "Hydrae",
    "Hyi": "Hydri",
    "Ind": "Indi",
    "Lac": "Lacertae",
    "Leo": "Leonis",
    "LMi": "Leonis Minoris",
    "Lep": "Leporis",
    "Lib": "Librae",
    "Lup": "Lupi",
    "Lyn": "Lyncis",
    "Lyr": "Lyrae",
    "Men": "Mensae",
    "Mic": "Microscopii",
    "Mon": "Monocerotis",
    "Mus": "Muscae",
    "Nor": "Normae",
    "Oct": "Octantis",
    "Oph": "Ophiuchi",
    "Ori": "Orionis",
    "Pav": "Pavonis",
    "Peg": "Pegasi",
    "Per": "Persei",
    "Phe": "Phoenicis",
    "Pic": "Pictoris",
    "Pis": "Piscium",
    "PsA": "Piscis Austrini",
    "Pup": "Puppis",
    "Pyx": "Pyxidis",
    "Ret": "Reticuli",
    "Sge": "Sagittae",
    "Sgr": "Sagittarii",
    "Sco": "Scorpii",
    "Scl": "Sculptoris",
    "Sct": "Scuti",
    "Ser": "Serpentis",
    "Sex": "Sextantis",
    "Tau": "Tauri",
    "Tel": "Telescopii",
    "Tri": "Trianguli",
    "TrA": "Trianguli Australis",
    "Tuc": "Tucanae",
    "UMa": "Ursae Majoris",
    "UMi": "Ursae Minoris",
    "Vel": "Velorum",
    "Vir": "Virginis",
    "Vol": "Volantis",
    "Vul": "Vulpeculae"
}

greek_letters = {
    "alf": "Alpha",
    "alf01": "Alpha 1",
    "alf02": "Alpha 2",
    "bet": "Beta",
    "bet01": "Beta 1",
    "bet02": "Beta 2",
    "gam": "Gamma",
    "gam01": "Gamma 1",
    "gam02": "Gamma 2",
    "del": "Delta",
    "del01": "Delta 1",
    "del02": "Delta 2",
    "eps": "Epsilon",
    "zet": "Zeta",
    "zet01": "Zeta 1",
    "zet02": "Zeta 2",
    "eta": "Eta",
    "eta01": "Eta 1",
    "eta02": "Eta 2",
    "tet": "Theta",
    "iot": "Iota",
    "iot01": "Iota 1",
    "iot02": "Iota 2",
    "kap": "Kappa",
    "lam": "Lambda",
    "mu.": "Mu",
    "mu.01": "Mu 1",
    "mu.02": "Mu 2",
    "nu": "Nu",
    "xi": "Xi",
    "omi": "Omicron",
    "pi.": "Pi",
    "rho": "Rho",
    "sig": "Sigma",
    "tau": "Tau",
    "ups": "Upsilon",
    "phi": "Phi",
    "chi": "Chi",
    "psi": "Psi",
    "ome": "Omega"
}

ignored_stars = [
    'Alpha 2 Crux',
    'Gamma 1 Leonis',
    'Beta 1 Scorpii'
]

stars = simbad.get_bright_objects(3.0)
additional_stars = [
    '* eps Cas', # Segin
    '* lam Ori', # Meissa
    '* del UMa', # Megrez
    '* eps Cru', # Ginan
    '* tet Eri', # Acamar
    '* del01 Vel' # Alsephina
]

for star_name in additional_stars:
    star_details = simbad.get_star_details(star_name)
    if star_details is not None:
        stars.append(star_details)

# stars = [star for star in stars if star[0].startswith('*')]

to_remove = []
for star in stars:
    id = star['bayer_designation']
    last = id.split(' ')[-1]
    if len(last) == 1 and last.isalpha():
        # See if there's a star with the same base id
        base_id = id[:-1].strip()
        if any(s['bayer_designation'] == base_id for s in stars):
            # print("Removing star with parent object", star['bayer_designation'])
            to_remove.append(star)

for star in to_remove:
    stars.remove(star)

# Sort stars by the second word in the ID and then by the first word
stars.sort(key=lambda x: x['bayer_designation'].split(' ')[1].lower() + " " + x['bayer_designation'].split(' ')[0].lower())

for star in stars:
    split_bayer_designation = star['bayer_designation'].split(' ')
    full_bayer_designation = greek_letters[split_bayer_designation[0]] + " " + constellation_abbreviation_to_name[split_bayer_designation[1]]
    if full_bayer_designation in ignored_stars:
        continue
    name = star['proper_name']
    if name is None:
        name = full_bayer_designation

    ra = star['right_ascension']
    dec = star['declination']
    v_mag = star['v_magnitude']
    pm_ra = star['proper_motion_right_ascension']
    pm_dec = star['proper_motion_declination']
    color_index = star['color_index_bv']
    print(f"Star(\"{full_bayer_designation}\", \"{name}\", EquatorialCoordinate({dec}, {ra}), {v_mag}f, ProperMotion({pm_dec}, {pm_ra}), {(str(color_index) + 'f') if not np.isnan(color_index) else 'null'}),")