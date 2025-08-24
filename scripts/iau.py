import csv

star_names = None

# https://exopla.net/sternbilder/moderne-sternbilder/
constellations = [
    {
        "name": "Andromeda",
        "abbreviation": "And",
        "member_name": "Andromedae",
        "lines": [
            ["gam01", "bet", "del", "alf"],
            ["del", "eps", "zet", "eta"],
            ["del", "pi.", "iot", "kap", "lam"],
            ["iot", "omi"],
            ["bet", "pi."],
            ["bet", "mu.", "nu.", "phi", "ups Per"]
        ]
    },
    {
        "name": "Antila",
        "abbreviation": "Ant",
        "member_name": "Antilae",
        "lines": [
            ["iot", "alf", "eps"]
        ]
    },
    {
        "name": "Apus",
        "abbreviation": "Aps",
        "member_name": "Apodis",
        "lines": [
            ["gam", "bet", "del01", "alf"]
        ]
    },
    {
        "name": "Aquarius",
        "abbreviation": "Aqr",
        "member_name": "Aquarii",
        "lines": [
            ["eps", "mu.", "bet", "alf", "pi.", "zet", "gam",
             "alf", "tet", "rho", "lam", "tau", "del"],
            ["iot", "bet"],
            ["zet", "eta"],
            ["lam", "phi"]
        ]
    },
    {
        "name": "Aquila",
        "abbreviation": "Aql",
        "member_name": "Aquilae",
        "lines": [
            ["bet", "alf", "gam", "del", "lam"],
            ["tet", "eta", "del", "zet", "eps"],
            ["tet", "iot", "lam"],
            ["lam", "zet"]
        ]
    },
    {
        "name": "Ara",
        "abbreviation": "Ara",
        "member_name": "Arae",
        "lines": [
            ["tet", "alf", "kap", "eps01", "zet", "eta", "del", "gam"],
            ["bet", "alf"]
        ]
    },
    {
        "name": "Carina",
        "abbreviation": "Car",
        "member_name": "Carinae",
        "lines": [
            ["alf", "bet", "ome", "tet", "z", "y", "x",
                "u", "w", "iot", "eps", "chi", "gam02 Vel"],
            ["tet", "w"],
            ["iot", "del01 Vel"]
        ]
    },
    {
        "name": "Puppis",
        "abbreviation": "Pup",
        "member_name": "Puppis",
        "lines": [
            ["alf Car", "nu.", "pi.", "p", "l", "omi", "ksi", "m", "p"],
            ["ksi", "rho", "zet", "gam02 Vel"],
            ["zet", "bet Pyx"]
        ]
    },
    {
        "name": "Pyxis",
        "abbreviation": "Pyx",
        "member_name": "Pyxidis",
        "lines": [
            ["gam", "alf", "bet"]
        ]
    },
    {
        "name": "Vela",
        "abbreviation": "Vel",
        "member_name": "Velorum",
        "lines": [
            ["gam02", "del01", "kap", "phi", "mu.", "q", "psi", "lam", "gam02"]
        ]
    },
    {
        "name": "Aries",
        "abbreviation": "Ari",
        "member_name": "Arietis",
        "lines": [
            ["gam", "bet", "alf", "41"]
        ]
    },
    {
        "name": "Auriga",
        "abbreviation": "Aur",
        "member_name": "Aurigae",
        "lines": [
            ["alf", "del", "pi.", "bet", "tet", "bet Tau",
             "iot", "eta", "zet", "eps", "alf", "eta"],
            ["alf", "bet"]
        ]
    },
    {
        "name": "Boötes",
        "abbreviation": "Boo",
        "member_name": "Boötis",
        "lines": [
            ["zet", "alf", "eta", "tau"],
            ["alf", "eps", "del", "bet", "gam", "rho", "alf"],
            ["gam", "lam", "kap02", "tet", "lam"]
        ]
    },
    {
        "name": "Caelum",
        "abbreviation": "Cae",
        "member_name": "Caeli",
        "lines": [
            ["gam", "bet", "alf", "del"]
        ]
    },
    {
        "name": "Camelopardalis",
        "abbreviation": "Cam",
        "member_name": "Camelopardalis",
        "lines": [
            ["bet", "alf", "gam"]
        ]
    },
    {
        "name": "Cancer",
        "abbreviation": "Cnc",
        "member_name": "Cancri",
        "lines": [
            ["alf", "del", "bet"],
            ["del", "gam", "iot"],
        ]
    },
    {
        "name": "Canes Venatici",
        "abbreviation": "CVn",
        "member_name": "Canum Venaticorum",
        "lines": [
            ["alf02", "bet"]
        ]
    },
    {
        "name": "Canis Major",
        "abbreviation": "CMa",
        "member_name": "Canis Majoris",
        "lines": [
            ["eta", "del", "eps", "omi01", "nu.02", "bet", "alf", "del"],
            ["alf", "iot", "gam", "tet", "iot"]
        ]
    },
    {
        "name": "Canis Minor",
        "abbreviation": "CMi",
        "member_name": "Canis Minoris",
        "lines": [
            ["alf", "bet"]
        ]
    },
    {
        "name": "Capricornus",
        "abbreviation": "Cap",
        "member_name": "Capricorni",
        "lines": [
            ["alf02", "bet01", "psi", "ome", "zet",
             "eps", "del", "gam", "tet", "alf02"]
        ]
    },
    {
        "name": "Cassiopeia",
        "abbreviation": "Cas",
        "member_name": "Cassiopeiae",
        "lines": [
            ["eps", "del", "gam", "alf", "bet"]
        ]
    },
    {
        "name": "Centaurus",
        "abbreviation": "Cen",
        "member_name": "Centauri",
        "lines": [
            ["alf", "bet", "eps", "zet", "ups01", "phi", "eta", "kap"],
            ["phi", "chi", "psi", "tet", "nu.", "iot"],
            ["mu.", "zet", "gam", "sig", "del", "pi."],
            ["sig", "rho", "omi01"],
            ["eps", "gam"]
        ]
    },
    {
        "name": "Lupus",
        "abbreviation": "Lup",
        "member_name": "Lupi",
        "lines": [
            ["alf", "zet", "eps", "gam", "del", "bet"],
            ["gam", "eta", "phi01", "chi", "eta", "zet"]
        ]
    },
    {
        "name": "Cepheus",
        "abbreviation": "Cep",
        "member_name": "Cephei",
        "lines": [
            ["tet", "eta", "alf", "mu.", "eps", "zet", "del", "iot", "bet", "alf"],
            ["bet", "gam", "iot"]
        ]
    },
    {
        "name": "Cetus",
        "abbreviation": "Cet",
        "member_name": "Ceti",
        "lines": [
            ["alf", "lam", "mu.", "ksi02", "gam", "del", "omi",
             "zet", "tau", "bet", "iot", "eta", "tet", "zet"],
            ["alf", "gam"]
        ]
    },
    {
        "name": "Chamaeleon",
        "abbreviation": "Cha",
        "member_name": "Chamaeleontis",
        "lines": [
            ["alf", "tet", "gam", "eps", "bet", "del02", "gam"]
        ]
    },
    {
        "name": "Circinus",
        "abbreviation": "Cir",
        "member_name": "Circini",
        "lines": [
            ["gam", "alf", "bet"]
        ]
    },
    {
        "name": "Columba",
        "abbreviation": "Col",
        "member_name": "Columbae",
        "lines": [
            ["eps", "alf", "bet", "gam", "del"],
            ["bet", "eta"]
        ]
    },
    {
        "name": "Coma Berenices",
        "abbreviation": "Com",
        "member_name": "Comae Berenices",
        "lines": [
            ["alf", "bet", "gam"]
        ]
    },
    {
        "name": "Corona Australis",
        "abbreviation": "CrA",
        "member_name": "Coronae Australis",
        "lines": [
            ["tet", "del", "bet", "alf", "gam"]
        ]
    },
    {
        "name": "Corona Borealis",
        "abbreviation": "CrB",
        "member_name": "Coronae Borealis",
        "lines": [
            ["tet", "bet", "alf", "gam", "del", "eps", "iot"]
        ]
    },
    {
        "name": "Crater",
        "abbreviation": "Crt",
        "member_name": "Crateris",
        "lines": [
            ["eta", "zet", "gam", "bet", "alf", "del", "gam"],
            ["del", "eps", "tet"]
        ]
    },
    {
        "name": "Crux",
        "abbreviation": "Cru",
        "member_name": "Crucis",
        "lines": [
            ["alf", "gam"],
            ["bet", "del"]
        ]
    },
    {
        "name": "Cygnus",
        "abbreviation": "Cyg",
        "member_name": "Cygni",
        "lines": [
            ["bet01", "gam", "eps", "zet", "nu.",
             "alf", "omi02", "iot", "del", "gam"],
            ["iot", "kap"]
        ]
    },
    {
        "name": "Delphinus",
        "abbreviation": "Del",
        "member_name": "Delphini",
        "lines": [
            ["eps", "bet", "del", "gam02", "alf", "bet"]
        ]
    },
    {
        "name": "Dorado",
        "abbreviation": "Dor",
        "member_name": "Doradus",
        "lines": [
            # TODO: HD 40409 is between delta and beta on the way to zeta
            ["gam", "alf", "bet", "del", "zet", "alf"]
        ]
    },
    {
        "name": "Draco",
        "abbreviation": "Dra",
        "member_name": "Draconis",
        "lines": [
            ["lam", "kap", "alf", "iot", "tet", "eta", "zet",
             "phi", "del", "ksi", "nu.01", "bet", "gam", "ksi"],
            ["del", "eps"],
            ["phi", "chi"]
        ]
    },
    {
        "name": "Equuleus",
        "abbreviation": "Equ",
        "member_name": "Equulei",
        "lines": [
            ["alf", "del", "gam"]
        ]
    },
    {
        "name": "Eridanus",
        "abbreviation": "Eri",
        "member_name": "Eridani",
        "lines": [
            ["alf", "chi", "kap", "s", "iot", "tet", "e", "y", "g", "ups04", "d", "ups02", "ups01", "tau09", "tau08",
             "tau06", "tau05", "tau04", "tau03", "tau01", "eta", "eps", "del", "pi.", "gam", "omi02", "nu.", "mu.", "bet"]
        ]
    },
    {
        "name": "Fornax",
        "abbreviation": "For",
        "member_name": "Fornacis",
        "lines": [
            ["alf", "bet", "nu."]
        ]
    },
    {
        "name": "Gemini",
        "abbreviation": "Gem",
        "member_name": "Geminorum",
        "lines": [
            ["ksi", "lam", "del", "zet", "gam"],
            ["del", "ups", "iot", "tau", "eps", "mu.", "eta", "1"],
            ["eps", "nu."],
            ["tau", "tet"],
            ["tau", "alf"],
            ["ups", "bet"],
            ["ups", "kap"]
        ]
    },
    {
        "name": "Grus",
        "abbreviation": "Gru",
        "member_name": "Gruis",
        "lines": [
            ["gam", "lam", "mu.01", "del01", "bet", "eps", "zet"],
            ["del01", "alf", "bet"]
        ]
    },
    {
        "name": "Hercules",
        "abbreviation": "Her",
        "member_name": "Herculis",
        "lines": [
            ["chi", "phi", "tau", "sig", "eta", "zet", "bet", "gam", "ome", "h"],
            ["bet", "alf", "del", "lam", "mu.01", "ksi", "omi"],
            ["del", "eps", "zet"],
            ["eps", "pi.", "eta"],
            ["pi.", "rho", "tet", "iot"]
        ]
    },
    {
        "name": "Horologium",
        "abbreviation": "Hor",
        "member_name": "Horologii",
        "lines": [
            ["bet", "mu.", "zet", "eta", "iot", "alf"]
        ]
    },
    {
        "name": "Corvus",
        "abbreviation": "Crv",
        "member_name": "Corvi",
        "lines": [
            ["alf", "eps", "gam", "del", "bet", "eps"]
        ]
    },
    {
        "name": "Hydra",
        "abbreviation": "Hya",
        "member_name": "Hydrae",
        "lines": [
            ["pi.", "gam", "bet", "ksi", "bet Crt"],
            ["alf Crt", "nu.", "phi", "mu.", "lam", "ups01", "alf",
                "iot", "tet", "zet", "eps", "del", "sig", "eta", "rho"]
        ]
    },
    {
        "name": "Hydrus",
        "abbreviation": "Hyi",
        "member_name": "Hydri",
        "lines": [
            ["alf", "bet", "gam", "alf"]
        ]
    },
    {
        "name": "Indus",
        "abbreviation": "Ind",
        "member_name": "Indi",
        "lines": [
            ["alf", "eta", "bet", "del", "tet", "alf"]
        ]
    },
    {
        "name": "Lacerta",
        "abbreviation": "Lac",
        "member_name": "Lacertae",
        "lines": [
            # TODO: HIP 109754 before 1 on first line
            ["bet", "alf", "5", "11", "6", "1"],
            ["bet", "4", "5", "2", "6"]
        ]
    },
    {
        "name": "Leo",
        "abbreviation": "Leo",
        "member_name": "Leonis",
        "lines": [
            ["mu.", "kap", "lam", "eps", "eta", "alf"],
            ["eta", "tet", "iot", "sig"],
            ["tet", "bet", "del", "gam", "eta"],
            ["gam", "zet", "mu.", "eps"],
            ["del", "tet"]
        ]
    },
    {
        "name": "Leo Minor",
        "abbreviation": "LMi",
        "member_name": "Leonis Minoris",
        "lines": [
            ["bet", "21", "10"],
            ["21", "27", "28", "30", "46", "bet"]
        ]
    },
    {
        "name": "Lepus",
        "abbreviation": "Lep",
        "member_name": "Leporis",
        "lines": [
            ["tet", "del", "gam", "bet", "eps", "mu.", "alf", "zet", "eta", "tet"],
            ["alf", "bet"],
            ["mu.", "lam"],
            ["mu.", "kap"]
        ]
    },
    {
        "name": "Libra",
        "abbreviation": "Lib",
        "member_name": "Librae",
        "lines": [
            ["tau", "ups", "gam", "bet", "alf02", "gam"],
            ["alf02", "sig"]
        ]
    },
    {
        "name": "Lynx",
        "abbreviation": "Lyn",
        "member_name": "Lyncis",
        "lines": [
            # HIP 44700 between 38 and 10 Uma
            ["alf", "38", "10 UMa", "31", "21", "15", "2"]
        ]
    },
    {
        "name": "Lyra",
        "abbreviation": "Lyr",
        "member_name": "Lyrae",
        "lines": [
            ["alf", "eps02", "zet01", "del02", "gam", "bet", "zet01", "alf"]
        ]
    },
    # Mensa has no lines in the offical IAU catalog
    # Microsopium has no lines in the offical IAU catalog
    {
        "name": "Monoceros",
        "abbreviation": "Mon",
        "member_name": "Monocerotis",
        "lines": [
            ["alf", "zet", "del", "bet", "gam"],
            ["del", "18", "eps Mon A", "13", "18"],
            ["13", "15"]
        ]
    },
    {
        "name": "Musca",
        "abbreviation": "Mus",
        "member_name": "Muscae",
        "lines": [
            ["alf", "gam", "del", "bet", "alf", "eps", "lam"]
        ]
    },
    {
        "name": "Norma",
        "abbreviation": "Nor",
        "member_name": "Normae",
        "lines": [
            ["del", "eta", "gam02", "eps", "del"]
        ]
    },
    {
        "name": "Octans",
        "abbreviation": "Oct",
        "member_name": "Octantis",
        "lines": [
            ["del", "bet", "nu.", "del"]
        ]
    },
    {
        "name": "Ophiuchus",
        "abbreviation": "Oph",
        "member_name": "Ophiuchi",
        "lines": [
            ["alf", "kap", "lam", "del", "eps", "ups", "zet", "phi", "chi"],
            ["zet", "kap"],
            ["zet", "eta", "tet", "d"],
            ["eta", "bet", "alf"],
            ["bet", "gam", "nu."]
        ]
    },
    {
        "name": "Serpens",
        "abbreviation": "Ser",
        "member_name": "Serpentis",
        "lines": [
            ["tet01", "eta", "ksi", "eta Oph"],
            ["del Oph", "mu.", "eps", "alf", "del",
                "bet", "gam", "kap", "iot", "bet"]
        ]
    },
    {
        "name": "Orion",
        "abbreviation": "Ori",
        "member_name": "Orionis",
        "lines": [
            ["kap", "zet", "eps", "del", "eta", "bet"],
            ["zet", "alf", "gam", "del"],
            ["gam", "lam", "alf", "mu.", "nu.", "chi01", "chi02", "ksi", "mu."]
        ]
    },
    {
        "name": "Pavo",
        "abbreviation": "Pav",
        "member_name": "Pavonis",
        "lines": [
            ["alf", "del", "bet", "gam", "alf"],
            ["del", "eps"],
            ["del", "zet"],
            ["del", "kap", "pi.", "eta"],
            ["pi.", "ksi", "gam", "del"]
        ]
    },
    {
        "name": "Pegasus",
        "abbreviation": "Peg",
        "member_name": "Pegasi",
        "lines": [
            ["eps", "tet", "42", "alf", "gam", "alf And", "bet", "alf"],
            ["bet", "eta", "pi."],
            ["bet", "mu.", "lam", "iot", "kap"]
        ]
    },
    {
        "name": "Perseus",
        "abbreviation": "Per",
        "member_name": "Persei",
        "lines": [
            ["phi", "tet", "iot", "tau", "eta", "gam", "tau"],
            ["gam", "alf", "iot"],
            ["alf", "del", "c", "mu.", "b", "lam"],
            ["del", "eps", "ksi", "zet", "omi"],
            ["eps", "bet", "rho"],
            ["bet", "kap", "iot"]
        ]
    },
    {
        "name": "Phoenix",
        "abbreviation": "Phe",
        "member_name": "Phoenicis",
        "lines": [
            ["alf", "eps", "bet", "zet", "del", "gam", "nu.", "bet", "alf"]
        ]
    },
    {
        "name": "Pictor",
        "abbreviation": "Pic",
        "member_name": "Pictoris",
        "lines": [
            ["alf", "gam", "bet"]
        ]
    },
    {
        "name": "Pisces",
        "abbreviation": "Psc",
        "member_name": "Piscium",
        "lines": [
            ["phi", "ups", "tau", "phi", "eta", "omi", "alf", "nu.", "eps",
                "del", "ome", "iot", "tet", "gam", "kap", "lam", "iot"]
        ]
    },
    {
        "name": "Piscis Austrinus",
        "abbreviation": "PsA",
        "member_name": "Piscis Austrini",
        "lines": [
            ["iot", "tet", "mu.", "eps", "alf", "del", "gam", "bet", "mu.", "iot"]
        ]
    },
    {
        "name": "Reticulum",
        "abbreviation": "Ret",
        "member_name": "Reticuli",
        "lines": [
            ["alf", "eps", "iot", "del", "bet", "alf"]
        ]
    },
    {
        "name": "Sagitta",
        "abbreviation": "Sge",
        "member_name": "Sagittae",
        "lines": [
            ["alf", "del", "gam"],
            ["bet", "del"]
        ]
    },
    {
        "name": "Sagittarius",
        "abbreviation": "Sgr",
        "member_name": "Sagittarii",
        "lines": [
            ["eta", "eps", "gam02", "del", "lam", "mu."],
            ["lam", "phi", "del"],
            ["phi", "sig", "tau", "zet", "eps"],
            ["phi", "zet"],
            ["del", "eps"]
        ]
    },
    {
        "name": "Scorpius",
        "abbreviation": "Sco",
        "member_name": "Scorpii",
        "lines": [
            ["G", "lam", "ups", "kap", "iot01", "tet", "eta", "zet02", "zet01",
                "mu.01", "eps", "tau", "alf", "sig", "del", "pi.", "rho"],
            ["del", "bet", "nu."]
        ]
    },
    {
        "name": "Sculptor",
        "abbreviation": "Scl",
        "member_name": "Sculptoris",
        "lines": [
            ["alf", "iot", "del", "gam", "bet"]
        ]
    },
    {
        "name": "Scutum",
        "abbreviation": "Sct",
        "member_name": "Scuti",
        "lines": [
            ["bet", "alf", "gam", "del", "bet"]
        ]
    },
    {
        "name": "Sextans",
        "abbreviation": "Sex",
        "member_name": "Sextantis",
        "lines": [
            ["del", "bet", "alf", "gam"]
        ]
    },
    {
        "name": "Taurus",
        "abbreviation": "Tau",
        "member_name": "Tauri",
        "lines": [
            ["bet", "eps", "del", "gam", "tet02", "alf", "zet"],
            ["gam", "lam", "ksi", "nu."],
            ["omi", "10"]
        ]
    },
    {
        "name": "Telescopium",
        "abbreviation": "Tel",
        "member_name": "Telescopii",
        "lines": [
            ["zet", "alf", "eps"]
        ]
    },
    {
        "name": "Triangulum",
        "abbreviation": "Tri",
        "member_name": "Trianguli",
        "lines": [
            ["alf", "bet", "gam", "alf"]
        ]
    },
    {
        "name": "Triangulum Australe",
        "abbreviation": "TrA",
        "member_name": "Trianguli Australis",
        "lines": [
            ["alf", "bet", "eps", "gam", "alf"]
        ]
    },
    {
        "name": "Tucana",
        "abbreviation": "Tuc",
        "member_name": "Tucanae",
        "lines": [
            ["alf", "del", "eps", "zet", "bet01", "gam", "alf"]
        ]
    },
    {
        "name": "Ursa Major",
        "abbreviation": "UMa",
        "member_name": "Ursae Majoris",
        "lines": [
            ["eta", "zet", "eps", "del", "gam", "chi", "nu.", "ksi"],
            ["chi", "psi", "mu.", "lam"],
            ["gam", "bet", "ups", "tet", "kap", "iot"],
            ["ups", "omi", "h", "alf", "del"],
            ["alf", "bet"]
        ]
    },
    {
        "name": "Ursa Minor",
        "abbreviation": "UMi",
        "member_name": "Ursae Minoris",
        "lines": [
            ["alf", "del", "eps", "zet", "bet", "gam", "eta", "zet"]
        ]
    },
    {
        "name": "Virgo",
        "abbreviation": "Vir",
        "member_name": "Virginis",
        "lines": [
            ["109", "tau", "zet", "iot", "mu."],
            ["zet", "gam", "del", "eps"],
            ["gam", "tet", "alf"],
            ["gam", "eta", "omi", "nu.", "bet", "eta"]
        ]
    },
    {
        "name": "Volans",
        "abbreviation": "Vol",
        "member_name": "Volantis",
        "lines": [
            ["alf", "bet", "eps", "del", "gam02", "eps", "alf"]
        ]
    },
    {
        "name": "Vulpecula",
        "abbreviation": "Vul",
        "member_name": "Vulpeculae",
        "lines": [
            ["alf", "15"]
        ]
    }
]

proper_name_replacement = {
    '87108': 'Bake-eo'
}

def get_constellation_name(abbreviation, for_member=False):
    for constellation in constellations:
        if constellation['abbreviation'].lower() == abbreviation.lower():
            return constellation['member_name'] if for_member else constellation['name']
    return None

def get_constellation_star_ids():
    stars = set()
    for constellation in constellations:
        lines = constellation['lines']
        for line in lines:
            for point in line:
                stars.add(
                    f'* {point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip())
    return list(stars)


def get_constellations(bayer_designations):
    filtered_constellations = []
    for constellation in constellations:
        name = constellation['name']
        lines = constellation['lines']
        adjusted_lines = []
        for line in lines:
            new_lines = [bayer_designations[f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip(
            )] for point in line if f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip() in bayer_designations]
            if len(new_lines) != len(line):
                bayer = [point for point in line if f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip(
                ) in bayer_designations]
                missing = set(line) - set(bayer)
                print(f"Constellation {name} has missing points: {missing}.")
            if len(new_lines) < 2:
                print(
                    f"Constellation {name} has less than 2 points, skipping.")
                continue
            adjusted_lines.append(new_lines)
        filtered_constellations.append({
            "name": name,
            "lines": adjusted_lines
        })
    return filtered_constellations

def __load_star_names():
    global star_names
    # TODO: Download the file if it doesn't exist from https://exopla.net/star-names/modern-iau-star-names/
    if star_names is None:
        with open('source/iau/star-names.csv', 'r') as f:
            reader = csv.DictReader(f)
            star_names = {}
            for row in reader:
                name = proper_name_replacement.get(row['HIP'], row['proper names'])
                star_names[row['Designation']] = name
                star_names[f'HIP {row['HIP']}'] = name
    return star_names

def get_star_names():
    return __load_star_names()

def get_star_name(ids):
    star_names = get_star_names()
    for id in ids:
        cleaned_id = ' '.join(id.split())
        if cleaned_id in star_names:
            return star_names[cleaned_id]
        
    return None