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
      ["eps", "mu.", "bet", "alf", "pi.", "zet", "gam", "alf", "tet", "rho", "lam", "tau", "del"],
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
      ["alf", "del", "pi.", "bet", "tet", "bet Tau", "iot", "eta", "zet", "eps", "alf", "eta"],
      ["alf", "bet"]
    ]
  },
#   {
#     "name": "Puppis",
#     "abbreviation": "Pup",
#     "lines": [
#         ["zet", "pi.", "ksi", "pi.", "nu.", "tau", "sig", "zet"]
#     ]
#   },
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
          ["alf", "iot", "gam", "tet"]
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
          ["alf01", "bet01", "psi", "ome", "zet", "eps", "del", "gam", "tet", "alf01"]
      ]
  },
  {
      "name": "Cassiopeia",
      "abbreviation": "Cas",
      "lines": [
          ["eps", "del", "gam", "alf", "bet"]
      ]
  }
]


def get_constellation_star_ids():
    stars = set()
    for constellation in constellations:
        lines = constellation['lines']
        for line in lines:
            for point in line:
                stars.add(f'* {point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip())
    return list(stars)

def get_constellations(bayer_designations):
    filtered_constellations = []
    for constellation in constellations:
        name = constellation['name']
        lines = constellation['lines']
        adjusted_lines = []
        for line in lines:
            new_lines = [bayer_designations[f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip()] for point in line if f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip() in bayer_designations]
            if len(new_lines) != len(line):
                bayer = [point for point in line if f'{point} {constellation['abbreviation'] if len(point.split(' ')) == 1 else ''}'.strip() in bayer_designations]
                missing = set(line) - set(bayer)
                print(f"Constellation {name} has missing points: {missing}.")
            if len(new_lines) < 2:
                print(f"Constellation {name} has less than 2 points, skipping.")
                continue
            adjusted_lines.append(new_lines)
        filtered_constellations.append({
            "name": name,
            "lines": adjusted_lines
        })
    return filtered_constellations