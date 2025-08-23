from scripts import iau, simbad
import numpy as np

def get_full_bayer_designation(star):
    split_bayer_designation = star['bayer_designation'].split(' ')
    first = greek_letters[split_bayer_designation[0]] if split_bayer_designation[0] in greek_letters else split_bayer_designation[0]
    if first == split_bayer_designation[0]:
        print("Unknown greek letter:", first)
    second = constellation_abbreviation_to_name[split_bayer_designation[1]] if split_bayer_designation[1] in constellation_abbreviation_to_name else split_bayer_designation[1]
    if second == split_bayer_designation[1]:
        print("Unknown constellation:", second)

    return f"{first} {second}"

def get_hip_number(star):
    if star['hip_designation'] is None:
        return None
    hip = star['hip_designation']
    hip_number = ''.join(filter(str.isdigit, hip))
    return int(hip_number) if hip_number else None

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
    "Psc": "Piscium",
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
    "eps01": "Epsilon 1",
    "eps02": "Epsilon 2",
    "zet": "Zeta",
    "zet01": "Zeta 1",
    "zet02": "Zeta 2",
    "eta": "Eta",
    "eta01": "Eta 1",
    "eta02": "Eta 2",
    "tet": "Theta",
    "tet01": "Theta 1",
    "tet02": "Theta 2",
    "iot": "Iota",
    "iot01": "Iota 1",
    "iot02": "Iota 2",
    "kap": "Kappa",
    "kap01": "Kappa 1",
    "kap02": "Kappa 2",
    "lam": "Lambda",
    "mu.": "Mu",
    "mu.01": "Mu 1",
    "mu.02": "Mu 2",
    "nu": "Nu",
    "nu.": "Nu",
    "nu.01": "Nu 1",
    "nu.02": "Nu 2",
    "xi": "Xi",
    "omi": "Omicron",
    "omi01": "Omicron 1",
    "omi02": "Omicron 2",
    "pi.": "Pi",
    "rho": "Rho",
    "rho01": "Rho 1",
    "rho02": "Rho 2",
    "sig": "Sigma",
    "tau": "Tau",
    "tau01": "Tau 1",
    "tau02": "Tau 2",
    "tau03": "Tau 3",
    "tau04": "Tau 4",
    "tau05": "Tau 5",
    "tau06": "Tau 6",
    "tau07": "Tau 7",
    "tau08": "Tau 8",
    "tau09": "Tau 9",
    "ups": "Upsilon",
    "ups01": "Upsilon 1",
    "ups02": "Upsilon 2",
    "ups03": "Upsilon 3",
    "ups04": "Upsilon 4",
    "phi": "Phi",
    "phi01": "Phi 1",
    "phi02": "Phi 2",
    "chi": "Chi",
    "chi01": "Chi 1",
    "chi02": "Chi 2",
    "psi": "Psi",
    "ome": "Omega",
    "ksi": "Ksi",
    "ksi01": "Ksi 1",
    "ksi02": "Ksi 2",
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

additional_star_details = simbad.get_all_star_details(additional_stars)
for star_details in additional_star_details:
    stars.append(star_details)

constellation_star_ids = iau.get_constellation_star_ids()
constallation_stars = []
for star_id in constellation_star_ids:
    if not any(star['bayer_designation'] == star_id[2:] for star in stars):
        constallation_stars.append(star_id)

constellation_star_details = simbad.get_all_star_details(constallation_stars)
for star_details in constellation_star_details:
    stars.append(star_details)

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

star_kotlin = []
seen_hip_ids = set()

for star in stars:
    full_bayer_designation = get_full_bayer_designation(star)
    if full_bayer_designation in ignored_stars:
        continue
    name = star['proper_name']
    if name is None:
        name = full_bayer_designation

    ra = star['right_ascension']
    dec = star['declination']
    v_mag = star['v_magnitude']
    v_mag = v_mag if v_mag is not None and not np.isnan(v_mag) else 10
    pm_ra = star['proper_motion_right_ascension']
    pm_dec = star['proper_motion_declination']
    color_index = star['color_index_bv']
    color_index = color_index if color_index is not None and not np.isnan(color_index) else 0
    hip = get_hip_number(star)
    if hip in seen_hip_ids:
        continue
    seen_hip_ids.add(hip)
    star_kotlin.append(f"Star({hip}, \"{name}\", EquatorialCoordinate({dec}, {ra}), {v_mag}f, ProperMotion({pm_dec}, {pm_ra}), {color_index}f)")

with open('output/stars.kt', 'w') as f:
    f.write(',\n'.join(star_kotlin))

constellation_kotlin = []
constellations = iau.get_constellations({star['bayer_designation']: get_hip_number(star) for star in stars})
for constellation in constellations:
    name = constellation['name']
    lines = constellation['lines']
    if len(lines) == 0:
        continue
    formatted_lines = f'listOf({", ".join([f"listOf({", ".join([str(point) for point in line])})" for line in lines])})'
    constellation_kotlin.append(f"Constellation(\"{name}\", {formatted_lines})")

with open('output/constellations.kt', 'w') as f:
    f.write(',\n'.join(constellation_kotlin))
