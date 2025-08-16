from astroquery.simbad import Simbad
from astropy.coordinates import Angle
import numpy as np

magnitude_map = {
    'Acrux': 0.76,
    'Alsephina': 1.95,
    'Acamar': 3.2,
    'Mizar': 2.04,
    'Markeb': 2.48
}

color_index_map = {
    'Hadar': -0.23,
    'Acrux': -0.26,
    'Alsephina': 0.04,
    'Acamar': 0.128,
    'Mizar': 0.02,
    'Markeb': -0.2
}

proper_motion_ra_map = {
    'Acrab': -5.2
}

proper_motion_dec_map = {
    'Acrab': -24.04
}

def get_star_details(star_name):
    # Look up the object ID for the star name
    result_table = Simbad.query_objectids(star_name)
    main_id = result_table["id"].data[0]

    # Query SIMBAD for the main ID
    Simbad.add_votable_fields("flux(V)", "pmra", "pmdec", "flux(B)")
    result_table = Simbad.query_object(main_id)
    ra = Angle(result_table["ra"].data[0], unit='hourangle').degree
    dec = Angle(result_table["dec"].data[0], unit='deg').degree
    v_mag = result_table["V"].data[0]
    if np.ma.is_masked(v_mag):
        v_mag = magnitude_map.get(star_name, np.nan)

    pm_ra = result_table["pmra"].data[0]
    if np.ma.is_masked(pm_ra):
        pm_ra = proper_motion_ra_map.get(star_name, np.nan)
    pm_ra = pm_ra / (1000 * 3600)

    pm_dec = result_table["pmdec"].data[0]
    if np.ma.is_masked(pm_dec):
        pm_dec = proper_motion_dec_map.get(star_name, np.nan)
    pm_dec = pm_dec / (1000 * 3600)

    b_mag = result_table["B"].data[0]
    if np.ma.is_masked(b_mag):
        b_mag = np.nan

    color_index = b_mag - v_mag

    if np.isnan(color_index):
        color_index = color_index_map.get(star_name, np.nan)

    return float(ra), float(dec), float(v_mag), float(pm_ra), float(pm_dec), float(color_index)