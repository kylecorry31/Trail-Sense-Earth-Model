from timezonefinder import TimezoneFinder

tf = TimezoneFinder()

# List all tz names
zones = tf.timezone_names


def wrap(lon):
    if lon < 0:
        return lon + 360
    return lon

def delta_angle(a, b):
    angle1 = wrap(a - b)
    angle2 = wrap(b - a)
    return -angle1 if angle1 < angle2 else angle2

def western_longitude(locations):
    minimum = locations[0][0]
    min_delta = 360
    for lon, lat in locations:
        delta = delta_angle(locations[0][0] + 180, lon + 180)
        if delta < min_delta:
            minimum = lon
            min_delta = delta
    return minimum

def eastern_longitude(locations):
    maximum = locations[0][0]
    max_delta = -360
    for lon, lat in locations:
        delta = delta_angle(locations[0][0] + 180, lon + 180)
        if delta > max_delta:
            maximum = lon
            max_delta = delta
    return maximum

prefixes = [
    "Africa/",
    "America/",
    "Antarctica/",
    "Arctic/",
    "Asia/",
    "Atlantic/",
    "Australia/",
    "Europe/",
    "Indian/",
    "Pacific/",
]

print("private val zones = arrayOf<Array<Any>>(")
for zone in zones:
    # If the zone doesn't start with any of the prefixes, skip it
    if not any(zone.startswith(prefix) for prefix in prefixes):
        continue

    geom = tf.get_geometry(tz_name=zone, coords_as_pairs=True)

    # Flatten the geometry
    geom = [c for r in geom for c in r]
    geom = [c for r in geom for c in r]



    west = western_longitude(geom)
    east = eastern_longitude(geom)
    min_lat = min(lat for lon, lat in geom)
    max_lat = max(lat for lon, lat in geom)

    center_latitude = (min_lat + max_lat) / 2
    center_longitude = (west + east) / 2 if west < east else (west + east + 360) / 2

    # Center of the geometry
    center = [center_longitude, center_latitude]

    prefix = zone.split("/")[0] + "/"
    zone_with_prefix_replaced = zone.replace(prefix, '') 

    print(f"    arrayOf(\"{zone_with_prefix_replaced}\", {int(center[0])}, {int(center[1])}),")

print(")")

