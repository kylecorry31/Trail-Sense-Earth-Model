from astroquery.simbad import Simbad
from astropy.coordinates import Angle
import numpy as np
import csv

star_names = None

# TODO: This is only needed because binary stars are excluded I think
magnitude_map = {
    '* del01 Vel': 1.95,
    '* tet Eri': 3.2,
    '* alf Cru': 0.67,
    '* alf Her': 3.08,
    '* tet Hya': 3.88,
    '* eps02 Lyr': 4.63,
    '* bet Mus': 2.97,
    '* mu. Ori': 4.16,
    '* iot Per': 4.05,
    '* alf Psc': 3.81,
    '* ome Psc': 4.01,
    '* del Ser': 3.86,
    '* gam Sex': 5.06,
    '* zet UMa': 2.25,
    '* eta UMi': 4.95,
    '* gam Ari': 3.84,
    '* pi. Cen': 3.83,
    '* eps Cep': 4.19,
    '* gam Cep': 3.38,
    '* eps Cha': 4.88,
    '* gam Cir': 4.53,
    '* gam CrB': 3.81,
    '* nu.01 Dra': 4.87
}

color_index_map = {
    '* bet Cen': -0.23,
    '* del01 Vel': 0.04,
    '* tet Eri': 0.128,
    '* alf Cru': -0.26,
    '* alf Her': 1.45
}

proper_motion_ra_map = {
    '* bet Sco': -5.2
}

proper_motion_dec_map = {
    '* bet Sco': -24.04
}

proper_name_map = {
    '* bet Sco': 'Acrab',
    '* alf Cen': 'Rigil Kentaurus',
    '* gam Ari': 'Mesarthim',
}

hip_map = {
    '* bet Sco': 78820,
    '* alf01 Cru': 60718,
    '* alf Cen': 71683 # 71681
}

def get_id_of_type(ids, type):
    for id in ids:
        cleaned_id = ' '.join(id.split())
        if cleaned_id.startswith(type + ' '):
            return cleaned_id[len(type):].strip()
    return None

# TODO: Move to iau
def get_star_name(ids):
    global star_names
    # TODO: Download the file if it doesn't exist from https://exopla.net/star-names/modern-iau-star-names/
    if star_names is None:
        with open('source/iau/star-names.csv', 'r') as f:
            reader = csv.DictReader(f)
            star_names = {}
            for row in reader:
                star_names[row['Designation']] = row['proper names']
                star_names[f'HIP {row['HIP']}'] = row['proper names']
    
    for id in ids:
        cleaned_id = ' '.join(id.split())
        if cleaned_id in star_names:
            return star_names[cleaned_id]
        
    return None


def parse_object_details(row):
    # Name
    main_id = row['main_id']
    if isinstance(main_id, bytes):
        main_id = main_id.decode('utf-8', errors='ignore')
    main_id = str(main_id)

    ids_value = row['ids']
    ids_decoded = ids_value.decode('utf-8', errors='ignore') if isinstance(
        ids_value, (bytes, bytearray)) else str(ids_value)
    ids = [main_id] + [p.strip() for p in ids_decoded.split('|')]
    proper_name = get_star_name(ids) if main_id not in proper_name_map else proper_name_map[main_id]
    hip_designation = get_id_of_type(ids, 'HIP')
    if hip_designation is None and main_id in hip_map:
        hip_designation = f'{hip_map[main_id]}'
    # TODO: Binary stars?
    bayer_designation = get_id_of_type(ids, '*')

    # Coordinates
    ra_str = row['ra']
    dec_str = row['dec']

    # Photometry
    v_mag = row['v']
    if v_mag is None or np.ma.is_masked(v_mag):
        v_mag = magnitude_map.get(main_id, np.nan)
    
    if np.isnan(v_mag):
        print("No V mag for", main_id)

    b_mag = row['b']
    if b_mag is None or np.ma.is_masked(b_mag):
        b_mag = np.nan

    # Color index (B - V)
    color_index = b_mag - \
        v_mag if not (np.isnan(b_mag) or np.isnan(v_mag)) else np.nan
    if np.isnan(color_index):
        color_index = color_index_map.get(main_id, np.nan)

    # Proper motion (convert mas/yr to deg/yr)
    pm_ra = row['pmra']
    if pm_ra is None or np.ma.is_masked(pm_ra):
        pm_ra = proper_motion_ra_map.get(main_id, np.nan)
    pm_dec = row['pmdec']
    if pm_dec is None or np.ma.is_masked(pm_dec):
        pm_dec = proper_motion_dec_map.get(main_id, np.nan)

    if not np.isnan(pm_ra):
        pm_ra = pm_ra / (1000 * 3600)
    if not np.isnan(pm_dec):
        pm_dec = pm_dec / (1000 * 3600)
    
    if bayer_designation is None or hip_designation is None:
        # print("No valid designation for", main_id)
        return None
    
    return {
        'object_type': None, # TODO: Figure out how to determine this
        'bayer_designation': bayer_designation,
        'hip_designation': hip_designation,
        'proper_name': proper_name, # Load this from the IAU list
        'right_ascension': float(ra_str),
        'declination': float(dec_str),
        'v_magnitude': float(v_mag),
        'proper_motion_right_ascension': float(pm_ra) if not np.isnan(pm_ra) else None,
        'proper_motion_declination': float(pm_dec) if not np.isnan(pm_dec) else None,
        'color_index_bv': float(color_index) if not np.isnan(color_index) else None
    }

# TODO: Merge this with the bright objects
def get_all_star_details(ids):
    # Query SIMBAD for the main ID
    Simbad.add_votable_fields("flux(V)", "pmra", "pmdec", "flux(B)")
    result_table = Simbad.query_objects(ids)

    objects = []
    if result_table is None or len(result_table) == 0:
        return objects
    
    # Build a case-insensitive column lookup
    colmap = {c.lower(): c for c in result_table.colnames}

    def col(name: str) -> str:
        return colmap.get(name.lower(), name)

    for row in result_table:
        new_row = {
            'main_id': row[col('MAIN_ID')],
            'ids': row[col('IDS')],
            'ra': row[col('RA')],
            'dec': row[col('DEC')],
            'v': row[col('V')] if col('V') in result_table.colnames else None,
            'b': row[col('B')] if col('B') in result_table.colnames else None,
            'pmra': row[col('PMRA')] if col('PMRA') in result_table.colnames else None,
            'pmdec': row[col('PMDEC')] if col('PMDEC') in result_table.colnames else None
        }

        obj = parse_object_details(new_row)

        if obj is None:
            continue
        objects.append(obj)

    return objects

def get_bright_objects(max_v_mag: float = 4.0):
    """
    Get all SIMBAD objects with V magnitude less than `max_v_mag` (default 4.0).
    """
    # Ensure needed fields are present (include IDS for common names)
    Simbad.add_votable_fields("flux(V)", "flux(B)", "pmra", "pmdec", "ids")

    # Query by V magnitude criterion
    result_table = Simbad.query_criteria(f"Vmag < {max_v_mag}")

    objects = []
    if result_table is None or len(result_table) == 0:
        return objects

    # Build a case-insensitive column lookup
    colmap = {c.lower(): c for c in result_table.colnames}

    def col(name: str) -> str:
        return colmap.get(name.lower(), name)

    for row in result_table:
        new_row = {
            'main_id': row[col('MAIN_ID')],
            'ids': row[col('IDS')],
            'ra': row[col('RA')],
            'dec': row[col('DEC')],
            'v': row[col('V')] if col('V') in result_table.colnames else None,
            'b': row[col('B')] if col('B') in result_table.colnames else None,
            'pmra': row[col('PMRA')] if col('PMRA') in result_table.colnames else None,
            'pmdec': row[col('PMDEC')] if col('PMDEC') in result_table.colnames else None
        }
        obj = parse_object_details(new_row)

        if obj is None:
            continue
        objects.append(obj)

    return objects
