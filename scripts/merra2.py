import os
from pydap.client import open_url
from scripts import to_tif
from scripts.progress import progress
import earthaccess

# Dew point / humidity might be retrieved from here: https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/hyrax/MERRA2_MONTHLY/M2TMNXSLV.5.12.4/2022/contents.html

temperature_offset = -273.15
source_folder = 'source/merra2'
credentials_file = 'nasa-credentials.txt'

def __get_version(year, month):
    revisions = [
        (2020, 9, 401),
        (2021, 6, 401),
        (2021, 7, 401),
        (2021, 8, 401),
        (2021, 9, 401),
    ]

    for revision in revisions:
        if year == revision[0] and month == revision[1]:
            return revision[2]

    if year <= 1991:
        return 100
    elif year < 2001:
        return 200
    elif year < 2011:
        return 300
    else:
        return 400

def __get_data(year, month, data_point):
    version = __get_version(year, month)
    dataset_url = f'https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_MONTHLY/M2SMNXSLV.5.12.4/{year}/MERRA2_{version}.statM_2d_slv_Nx.{year}{str(month).zfill(2)}.nc4?{data_point}'
    session = earthaccess.get_requests_https_session()
    data = open_url(dataset_url, session=session)
    session.close()
    values = data[data_point][0, :, :][0]
    values = [[float(x) + temperature_offset for x in value] for value in values]
    return values

def __write_img(year, month, values, data_point):
    to_tif(values, f'{source_folder}/{year}-{month}-{data_point}.tif', is_inverted=True)

def download(start_year=1991, end_year=2020, redownload = False):
    data_points = ['T2MMIN', 'T2MMAX']
    missing = [
        (year, month, data_point)
        for data_point in data_points
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
        if not os.path.exists(f'{source_folder}/{year}-{month}-{data_point}.tif')
    ]
    if not missing and not redownload:
        return

    if not os.path.exists(credentials_file):
        username = input("NASA Earthdata username: ")
        password = input("NASA Earthdata password: ")
        with open(credentials_file, 'w') as f:
            f.write(username + '\n')
            f.write(password + '\n')
    
    with open(credentials_file, 'r') as f:
        username = f.readline().strip()
        password = f.readline().strip()
    
    os.environ['EARTHDATA_USERNAME'] = username
    os.environ['EARTHDATA_PASSWORD'] = password
    earthaccess.login()

    # TODO: download both T2MMIN and T2MMAX at the same time
    with progress("Downloading MERRA-2 data", (end_year - start_year + 1) * 12 * len(data_points)) as pbar:
        for data_point in data_points:
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    if not os.path.exists(f'{source_folder}/{year}-{month}-{data_point}.tif') or redownload:
                        values = __get_data(year, month, data_point)
                        __write_img(year, month, values, data_point)
                    pbar.update(1)
