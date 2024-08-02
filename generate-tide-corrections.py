from scripts import tidal_corrections

# INPUT
year = 2025

######## Program, don't modify ########
corrections = tidal_corrections.get_corrections(year)
print(corrections)