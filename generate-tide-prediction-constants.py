from scripts import noaa

# INPUT
station_id = "8452660" # Optional, set to None and provide location to get closest station
location = (41.4763, -71.3216) # Optional, set to None and provide station_id

######## Program, don't modify ########
if not station_id:
    station = noaa.get_closest_station(location[0], location[1])
    print(f"{station[1]}, {station[2]}")
    print()
    station_id = station[0]

lunitidal_interval = noaa.get_lunitidal_interval(station_id)
print(f"LUNITIDAL INTERVAL:\n{lunitidal_interval[0]} (low), {lunitidal_interval[1]} (high)")
print()

print("HARMONICS:")
harmonics = noaa.get_harmonic_constituents(station_id)
print(harmonics)
