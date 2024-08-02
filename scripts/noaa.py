import requests
import json

def get_closest_station(latitude, longitude):
    url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json"
    response = requests.get(url)
    data = json.loads(response.text)

    closest_station = None
    closest_distance = 1e9
    for station in data["stations"]:
        station_latitude = station["lat"]
        station_longitude = station["lng"]
        distance = (latitude - station_latitude) ** 2 + (longitude - station_longitude) ** 2
        if distance < closest_distance:
            closest_station = station
            closest_distance = distance
        
    return (closest_station["id"], closest_station["name"], closest_station["state"])

def get_harmonic_constituents(station_id):
    url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}/harcon.json"

    # TODO: Load MTL/MLLW from the station metadata (MTL - MLLW)

    response = requests.get(url)
    data = json.loads(response.text)

    units = data["units"]
    # if units is feet, convert to meters
    amplitude_to_meters = 0.3048 if units == "feet" else 1

    constituents = []
    for constituent in data["HarmonicConstituents"]:
        constituents.append(
            {
                "number": constituent["number"],
                "amplitude": constituent["amplitude"] * amplitude_to_meters,
                "phase": constituent["phase_GMT"],
            }
        )

    z0 = get_z0(station_id)
    constituents.append({
        "number": 0,
        "amplitude": z0,
        "phase": 0
    })

    constituents = list(sorted(constituents, key=lambda x: x["number"]))

    return "Constituent,Amplitude,Phase\n" + "\n".join([ f"{c['number']},{c['amplitude']},{c['phase']}" for c in constituents ])

def get_lunitidal_interval(station_id):
    url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}/datums.json"

    response = requests.get(url)
    data = json.loads(response.text)

    low = None
    high = None

    for datum in data["datums"]:
        if datum["name"] == "LWI":
            low = datum["value"]
        if datum["name"] == "HWI":
            high = datum["value"]

    return (low, high)

def get_z0(station_id):
    url = f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}/datums.json"

    response = requests.get(url)
    data = json.loads(response.text)

    units = data["units"]
    # if units is feet, convert to meters
    amplitude_to_meters = 0.3048 if units == "feet" else 1

    mtl = None
    mllw = None

    for datum in data["datums"]:
        if datum["name"] == "MTL":
            mtl = datum["value"] * amplitude_to_meters
        
        if datum["name"] == "MLLW":
            mllw = datum["value"] * amplitude_to_meters

    return mtl - mllw