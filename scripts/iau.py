import json


# https://exopla.net/sternbilder/moderne-sternbilder/
constellations = [
    {
        "name": "Andromeda",
        "abbreviation": "And",
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
        "lines": [
            ["iot", "alf", "eps"]
        ]
    },
    {
        "name": "Apus",
        "abbreviation": "Aps",
        "lines": [
            ["gam", "bet", "del01", "alf"]
        ]
    },
    {
        "name": "Aquarius",
        "abbreviation": "Aqr",
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
        "lines": [
            ["tet", "alf", "kap", "eps01", "zet", "eta", "del", "gam"],
            ["bet", "alf"]
        ]
    },
    #   {
    #     "name": "Carina",
    #     "abbreviation": "Car",
    #     "lines": [
    #         ["alf", "bet", "ome", "tet"]
    #     ]
    #   }
    # Puppis
    # Pyxis
    # Vela
    {
        "name": "Aries",
        "abbreviation": "Ari",
        "lines": [
            ["gam", "bet", "alf", "41"]
        ]
    },
    {
        "name": "Auriga",
        "abbreviation": "Aur",
        "lines": [
            ["alf", "del", "pi.", "bet", "tet", "bet Tau",
             "iot", "eta", "zet", "eps", "alf", "eta"],
            ["alf", "bet"]
        ]
    },
    {
        "name": "Boötes",
        "abbreviation": "Boo",
        "lines": [
            ["zet", "alf", "eta", "tau"],
            ["alf", "eps", "del", "bet", "gam", "rho", "alf"],
            ["gam", "lam", "kap02", "tet", "lam"]
        ]
    },
    {
        "name": "Caelum",
        "abbreviation": "Cae",
        "lines": [
            ["gam", "bet", "alf", "del"]
        ]
    },
    {
        "name": "Camelopardalis",
        "abbreviation": "Cam",
        "lines": [
            ["bet", "alf", "gam"]
        ]
    },
    {
        "name": "Cancer",
        "abbreviation": "Cnc",
        "lines": [
            ["alf", "del", "bet"],
            ["del", "gam", "iot"],
        ]
    },
    {
        "name": "Canes Venatici",
        "abbreviation": "CVn",
        "lines": [
            ["alf02", "bet"]
        ]
    },
    {
        "name": "Canis Major",
        "abbreviation": "CMa",
        "lines": [
            ["eta", "del", "eps", "omi01", "nu.02", "bet", "alf", "del"],
            ["alf", "iot", "gam", "tet", "iot"]
        ]
    },
    {
        "name": "Canis Minor",
        "abbreviation": "CMi",
        "lines": [
            ["alf", "bet"]
        ]
    },
    {
        "name": "Capricornus",
        "abbreviation": "Cap",
        "lines": [
            ["alf01", "bet01", "psi", "ome", "zet",
             "eps", "del", "gam", "tet", "alf01"]
        ]
    },
    {
        "name": "Cassiopeia",
        "abbreviation": "Cas",
        "lines": [
            ["eps", "del", "gam", "alf", "bet"]
        ]
    },
    {
        "name": "Centaurus",
        "abbreviation": "Cen",
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
        "lines": [
            ["alf", "zet", "eps", "gam", "del", "bet"],
            ["gam", "eta", "phi01", "chi", "eta", "zet"]
        ]
    },
    {
        "name": "Cepheus",
        "abbreviation": "Cep",
        "lines": [
            ["tet", "eta", "alf", "mu.", "eps", "zet", "del", "iot", "bet", "alf"],
            ["bet", "gam", "iot"]
        ]
    },
    {
        "name": "Cetus",
        "abbreviation": "Cet",
        "lines": [
            ["alf", "lam", "mu.", "ksi02", "gam", "del", "omi",
             "zet", "tau", "bet", "iot", "eta", "tet", "zet"],
            ["alf", "gam"]
        ]
    },
    {
        "name": "Chamaeleon",
        "abbreviation": "Cha",
        "lines": [
            ["alf", "tet", "gam", "eps", "bet", "del02", "gam"]
        ]
    },
    {
        "name": "Circinus",
        "abbreviation": "Cir",
        "lines": [
            ["gam", "alf", "bet"]
        ]
    },
    {
        "name": "Columba",
        "abbreviation": "Col",
        "lines": [
            ["eps", "alf", "bet", "gam", "del"],
            ["bet", "eta"]
        ]
    },
    {
        "name": "Coma Berenices",
        "abbreviation": "Com",
        "lines": [
            ["alf", "bet", "gam"]
        ]
    },
    {
        "name": "Corona Australis",
        "abbreviation": "CrA",
        "lines": [
            ["tet", "del", "bet", "alf", "gam"]
        ]
    },
    {
        "name": "Corona Borealis",
        "abbreviation": "CrB",
        "lines": [
            ["tet", "bet", "alf", "gam", "del", "eps", "iot"]
        ]
    },
    {
        "name": "Crater",
        "abbreviation": "Crt",
        "lines": [
            ["eta", "zet", "gam", "bet", "alf", "del", "gam"],
            ["del", "eps", "tet"]
        ]
    },
    {
        "name": "Crux",
        "abbreviation": "Cru",
        "lines": [
            ["alf", "gam"],
            ["bet", "del"]
        ]
    },
    {
        "name": "Cygnus",
        "abbreviation": "Cyg",
        "lines": [
            ["bet01", "gam", "eps", "zet", "nu.",
             "alf", "omi02", "iot", "del", "gam"],
            ["iot", "kap"]
        ]
    },
    {
        "name": "Delphinus",
        "abbreviation": "Del",
        "lines": [
            ["eps", "bet", "del", "gam02", "alf", "bet"]
        ]
    },
    {
        "name": "Dorado",
        "abbreviation": "Dor",
        "lines": [
            # TODO: HD 40409 is between delta and beta on the way to zeta
            ["gam", "alf", "bet", "del", "zet", "alf"]
        ]
    },
    {
        "name": "Draco",
        "abbreviation": "Dra",
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
        "lines": [
            ["alf", "del", "gam"]
        ]
    },
    {
        "name": "Eridanus",
        "abbreviation": "Eri",
        # TODO: upsilon 3 eri between ups 04 and ups 02
        "lines": [
            ["alf", "chi", "kap", "s", "iot", "tet", "e", "y", "g", "ups04", "ups02", "ups01", "tau09", "tau08",
             "tau06", "tau05", "tau04", "tau03", "tau01", "eta", "eps", "del", "pi.", "gam", "omi02", "nu.", "mu.", "bet"]
        ]
    },
    {
        "name": "Fornax",
        "abbreviation": "For",
        "lines": [
            ["alf", "bet", "nu."]
        ]
    },
    {
        "name": "Gemini",
        "abbreviation": "Gem",
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
        "lines": [
            ["gam", "lam", "mu.01", "del01", "bet", "eps", "zet"],
            ["del01", "alf", "bet"]
        ]
    },
    {
        "name": "Hercules",
        "abbreviation": "Her",
        "lines": [
            # TODO: 29 hercules in first list after ome
            ["chi", "phi", "tau", "sig", "eta", "zet", "bet", "gam", "ome"],
            ["bet", "alf", "del", "lam", "mu.01", "ksi", "omi"],
            ["del", "eps", "zet"],
            ["eps", "pi.", "eta"],
            ["pi.", "rho", "tet", "iot"]
        ]
    },
    {
        "name": "Horologium",
        "abbreviation": "Hor",
        "lines": [
            ["bet", "mu.", "zet", "eta", "iot", "alf"]
        ]
    },
    {
        "name": "Corvus",
        "abbreviation": "Crv",
        "lines": [
            ["alf", "eps", "gam", "del", "bet", "eps"]
        ]
    },
    {
        "name": "Hydra",
        "abbreviation": "Hya",
        "lines": [
            # TODO: IAU shows this as connecting to Crater between ksi and nu
            ["pi.", "gam", "bet", "ksi", "nu.", "phi", "mu.", "lam", "ups01", "alf", "iot", "tet", "zet", "eps", "del", "sig", "eta", "rho"]
        ]   
    },
    {
        "name": "Hydrus",
        "abbreviation": "Hyi",
        "lines": [
            ["alf", "bet", "gam", "alf"]
        ]
    },
    {
        "name": "Indus",
        "abbreviation": "Ind",
        "lines": [
            ["alf", "eta", "bet", "del", "tet", "alf"]
        ]
    },
    {
        "name": "Lacerta",
        "abbreviation": "Lac",
        "lines": [
            # TODO: HIP 109754 before 1 on first line
            ["bet", "alf", "5", "11", "6", "1"],
            ["bet", "4", "5", "2", "6"]
        ]
    },
    {
        "name": "Leo",
        "abbreviation": "Leo",
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
        "lines": [
            ["bet", "10", "21"],
            ["21", "27", "28", "30", "46", "bet"]
        ]
    },
    {
        "name": "Lepus",
        "abbreviation": "Lep",
        "lines": [
            ["tet", "del", "gam", "bet", "eps", "mu.", "alf", "zet", "eta", "tet"],
            ["alf", "bet"],
            ["mu.", "gam"],
            ["mu.", "kap"]
        ]
    },
    {
        "name": "Libra",
        "abbreviation": "Lib",
        "lines": [
            ["tau", "ups", "gam", "bet", "alf02", "gam"],
            ["alf02", "sig"]
        ]
    },
    {
        "name": "Lynx",
        "abbreviation": "Lyn",
        "lines": [
            # HIP 44700 between 38 and 10 Uma
            ["alf", "38", "10 UMa", "31", "21", "15", "2"]
        ]
    },
    {
        "name": "Lyra",
        "abbreviation": "Lyr",
        "lines": [
            ["alf", "eps02", "zet01", "del02", "gam", "bet", "zet01", "alf"]
        ]
    },
    # Mensa has no lines in the offical IAU catalog
    # Microsopium has no lines in the offical IAU catalog
    {
        "name": "Monoceros",
        "abbreviation": "Mon",
        "lines": [
            ["alf", "zet", "del", "bet", "gam"],
            ["del", "18", "eps Mon A", "13", "18"],
            ["13", "15"]
        ]
    },
    {
        "name": "Musca",
        "abbreviation": "Mus",
        "lines": [
            ["gam", "eps", "alf", "bet", "del", "gam", "alf"]
        ]
    },
    {
        "name": "Norma",
        "abbreviation": "Nor",
        "lines": [
            ["del", "eta", "gam02", "eps", "del"]
        ]
    },
    {
        "name": "Octans",
        "abbreviation": "Oct",
        "lines": [
            ["del", "bet", "nu."]
        ]
    },
    {
        "name": "Ophiuchus",
        "abbreviation": "Oph",
        "lines": [
            ["alf", "kap", "lam", "del", "eps", "ups", "zet", "phi", "chi"],
            ["del", "kap"],
            # Ends with 45 Oph, but there's no HIP designation
            ["zet", "eta", "tet"],
            ["eta", "bet", "alf"],
            ["bet", "gam", "nu."]
        ]        
    },
    {
        "name": "Serpens",
        "abbreviation": "Ser",
        "lines": [
            ["tet01", "eta", "ksi", "eta Oph"],
            ["del Oph", "mu.", "eps", "alf", "del", "bet", "gam", "kap", "iot", "bet"]
        ]
    },
    {
        "name": "Orion",
        "abbreviation": "Ori",
        "lines": [
            ["kap", "zet", "eps", "del", "eta", "bet"],
            ["zet", "alf", "gam", "del"],
            ["gam", "lam", "alf", "mu.", "nu.", "chi01", "chi02", "ksi", "mu."]
        ]
    },
    {
        "name": "Pavo",
        "abbreviation": "Pav",
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
        "lines": [
            ["eps", "tet", "42", "alf", "gam", "alf And", "bet", "alf"],
            ["bet", "eta", "pi."],
            ["bet", "mu.", "lam", "iot", "kap"]
        ]
    },
    {
        "name": "Perseus",
        "abbreviation": "Per",
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
        "lines": [
            ["alf", "eps", "bet", "zet", "del", "gam", "nu.", "bet", "alf"]
        ]
    },
    {
        "name": "Pictor",
        "abbreviation": "Pic",
        "lines": [
            ["alf", "gam", "bet"]
        ]
    }
]


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
