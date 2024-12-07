from astroquery.simbad import Simbad
from astropy.coordinates import Angle
import numpy as np

magnitude_map = {
    'Acrux': 0.76,
    'Alsephina': 1.95,
    'Acamar': 3.2,
    'Mizar': 2.04
}

def get_star_details(star_name):
    # Look up the object ID for the star name
    result_table = Simbad.query_objectids(star_name)
    main_id = result_table["ID"].data[0].decode("utf-8")

    # Query SIMBAD for the main ID
    Simbad.add_votable_fields("flux(V)", "pmra", "pmdec")
    result_table = Simbad.query_object(main_id)
    ra = Angle(result_table["RA"].data[0], unit='hourangle').degree
    dec = Angle(result_table["DEC"].data[0], unit='deg').degree
    v_mag = result_table["FLUX_V"].data[0]
    if np.ma.is_masked(v_mag):
        v_mag = magnitude_map.get(star_name, np.nan)

    pm_ra = result_table["PMRA"].data[0] / (1000 * 3600)
    pm_dec = result_table["PMDEC"].data[0] / (1000 * 3600)

    return float(ra), float(dec), float(v_mag), float(pm_ra), float(pm_dec)