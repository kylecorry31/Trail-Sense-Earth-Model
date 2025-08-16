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
    '* bet Cen': -0.23,
    'Hadar': -0.23,
    'Acrux': -0.26,
    'Alsephina': 0.04,
    'Acamar': 0.128,
    'Mizar': 0.02,
    'Markeb': -0.2
}

proper_motion_ra_map = {
    'Acrab': -5.2,
    '* bet Sco': -5.2
}

proper_motion_dec_map = {
    'Acrab': -24.04,
    '* bet Sco': -24.04
}

main_id_map = {
    'Mizar': '* zet01 UMa',
    'Markeb': 'CD-26 4707',
    'Girtab': '* kap Sco',
    'Muhlifain': '* gam Cen',
    'Uridim': '* alf Lup'
}

def get_star_details(star_name):
    # Look up the object ID for the star name
    if star_name in main_id_map:
        main_id = main_id_map[star_name]
    else:
        result_table = Simbad.query_objectids(star_name)
        main_id = result_table["id"].data[0]

    # Query SIMBAD for the main ID
    Simbad.add_votable_fields("flux(V)", "pmra", "pmdec", "flux(B)")
    result_table = Simbad.query_object(main_id)
    ra = Angle(result_table["ra"].data[0], unit='deg').degree
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

    return main_id, float(ra), float(dec), float(v_mag), float(pm_ra), float(pm_dec), float(color_index)

def get_bright_objects(max_v_mag: float = 4.0):
    """
    Get all SIMBAD objects with V magnitude less than `max_v_mag` (default 4.0).

    Returns a list of tuples:
      (name, principal_name, ra_deg, dec_deg, v_mag, pm_ra_deg_per_yr, pm_dec_deg_per_yr, color_index_b_minus_v)
    where `name` is a user-readable common name when available (from IDS -> 'NAME <X>').
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

    def extract_common_name(ids_value) -> str:
        try:
            if ids_value is None or (hasattr(ids_value, 'mask') and getattr(ids_value, 'mask', False)):
                raise ValueError
            s = ids_value.decode('utf-8', errors='ignore') if isinstance(ids_value, (bytes, bytearray)) else str(ids_value)
            parts = [p.strip() for p in s.split('|')]
            names = [p[4:].strip() for p in parts if p.upper().startswith('NAME ')]
            return names
        except Exception:
            pass
        return []

    for row in result_table:
        # Principal (main) identifier
        main_id = row[col('MAIN_ID')]
        if isinstance(main_id, bytes):
            main_id = main_id.decode('utf-8', errors='ignore')
        main_id = str(main_id)

        # Common/user-readable name from IDS
        ids_value = row[col('IDS')] if col('IDS') in result_table.colnames else None
        names = extract_common_name(ids_value)

        # Coordinates
        ra_str = row[col('RA')]
        dec_str = row[col('DEC')]
        ra = Angle(ra_str, unit='hourangle').degree
        dec = Angle(dec_str, unit='deg').degree

        # Photometry
        v_mag = row[col('V')] if col('V') in result_table.colnames else np.nan
        if np.ma.is_masked(v_mag):
            v_mag = np.nan

        b_mag = row[col('B')] if col('B') in result_table.colnames else np.nan
        if np.ma.is_masked(b_mag):
            b_mag = np.nan

        # Color index (B - V)
        color_index = b_mag - v_mag if not (np.isnan(b_mag) or np.isnan(v_mag)) else np.nan
        if np.isnan(color_index):
            color_index = color_index_map.get(main_id, np.nan)

        # Proper motion (convert mas/yr to deg/yr)
        pm_ra = row[col('PMRA')] if col('PMRA') in result_table.colnames else np.nan
        if np.ma.is_masked(pm_ra):
            pm_ra = proper_motion_ra_map.get(main_id, np.nan)
        pm_dec = row[col('PMDEC')] if col('PMDEC') in result_table.colnames else np.nan
        if np.ma.is_masked(pm_dec):
            pm_dec = proper_motion_dec_map.get(main_id, np.nan)

        if not np.isnan(pm_ra):
            pm_ra = pm_ra / (1000 * 3600)
        if not np.isnan(pm_dec):
            pm_dec = pm_dec / (1000 * 3600)

        objects.append((main_id, names, float(ra), float(dec), float(v_mag),
                        float(pm_ra) if not np.isnan(pm_ra) else np.nan,
                        float(pm_dec) if not np.isnan(pm_dec) else np.nan,
                        float(color_index) if not np.isnan(color_index) else np.nan))

    return objects