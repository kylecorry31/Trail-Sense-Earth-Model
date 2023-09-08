import PIL.Image as Image
import os
from pydap.client import open_url
from pydap.cas.urs import setup_session
from scripts import to_tif, load_pixels
from scripts.progress import progress

# Dew point / humidity might be retrieved from here: https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/hyrax/MERRA2_MONTHLY/M2TMNXSLV.5.12.4/2022/contents.html

temperature_offset = -273.15
elevation_invalid_value = -99999
elevation_image = 'images/dem-land-etopo.tif'
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

def __get_data_M2SMNXSLV(year, month, username, password, data_point):
    version = __get_version(year, month)
    dataset_url = f'https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_MONTHLY/M2SMNXSLV.5.12.4/{year}/MERRA2_{version}.statM_2d_slv_Nx.{year}{str(month).zfill(2)}.nc4?{data_point}'
    session = setup_session(username, password, check_url=dataset_url)
    data = open_url(dataset_url, session=session)
    session.close()
    values = data[data_point][0, :, :][0]
    values = [[float(x) + temperature_offset for x in value] for value in values]
    return values

def __get_data_M2TCNPLTM(month, username, password, data_point):
    month_str = str(month).zfill(2)
    dataset_url = f'https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_CLIM/M2TCNPLTM.1/1981/MERRA2.tavgC_3d_ltm_Np.1981{month_str}_2010{month_str}.nc4?{data_point}'
    session = setup_session(username, password, check_url=dataset_url)
    data = open_url(dataset_url, session=session)
    session.close()
    values = data[data_point][0, :, :][0][0]
    values = [[float(x) for x in value] for value in values]
    return values

def __write_img(year, month, values, data_point):
    to_tif(values, f'{source_folder}/{year}-{month}-{data_point}.tif', is_inverted=True)

def __to_sea_level(data, elevations):
    w = len(data[0])
    h = len(data)
    for y in range(h):
        for x in range(w):
            elevation_x = int(x / w * len(elevations[0]))
            elevation_y = int(y / h * len(elevations))
            elevation = elevations[elevation_y, elevation_x]
            if elevation == elevation_invalid_value:
                elevation = 0
            # Invert elevation to bring it back down to sea level
            data[y, x] = data[y, x] + 0.0065 * elevation
    return data

def __load_data(year, month, data_point):
    return load_pixels(f'source/merra2/{year}-{month}-{data_point}.tif')

def __write_img_processed(year, month, values, data_point):
    to_tif(values, f'images/{year}-{month}-{data_point}.tif')

# TODO: Split out temperature and humidity into separate functions
def download(start_year=1991, end_year=2020, redownload = False):
    if not os.path.exists(credentials_file):
        username = input("NASA Earthdata username: ")
        password = input("NASA Earthdata password: ")
        with open(credentials_file, 'w') as f:
            f.write(username + '\n')
            f.write(password + '\n')
    
    with open(credentials_file, 'r') as f:
        username = f.readline().strip()
        password = f.readline().strip()
    
    data_points = ['T2MMIN', 'T2MMAX']
    
    # TODO: download both T2MMIN and T2MMAX at the same time
    with progress("Downloading MERRA-2 data", (end_year - start_year + 1) * 12 * len(data_points) + 12) as pbar:
        for data_point in data_points:
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    if not os.path.exists(f'{source_folder}/{year}-{month}-{data_point}.tif') or redownload:
                        values = __get_data_M2SMNXSLV(year, month, username, password, data_point)
                        __write_img(year, month, values, data_point)
                    pbar.update(1)
        
        # Download the humdity data
        point = 'QV'
        for month in range(1, 13):
            if not os.path.exists(f'{source_folder}/1981-{month}-{point}.tif') or redownload:
                values = __get_data_M2TCNPLTM(month, username, password, point)
                __write_img(1981, month, values, point)
            pbar.update(1)  

def process_temperatures(start_year=1991, end_year=2020):
    data_points = ['T2MMIN', 'T2MMAX']
    Image.MAX_IMAGE_PIXELS = None
    with progress("Loading elevation data", 1) as pbar:
        elevations = load_pixels(elevation_image)
        pbar.update(1)
    
    for data_point in data_points:
        sum_values = []
        count_values = []
        # Calculate the climate normals
        with progress(f"Calculating climate normals ({data_point})", (end_year - start_year + 1) * 12) as pbar:
            for year in range(start_year, end_year + 1):
                for month in range(1, 13):
                    values = __to_sea_level(__load_data(year, month, data_point), elevations)
                    if len(sum_values) < month:
                        sum_values.append(values)
                        count_values.append(1)
                    else:
                        sum_values[month - 1] += values
                        count_values[month - 1] += 1
                    pbar.update(1)

        # Average the values
        for month in range(1, 13):
            sum_values[month - 1] = sum_values[month - 1] / count_values[month - 1]

        # Write the average values to a TIF file
        with progress(f"Generating images ({data_point})", 12) as pbar:
            for month in range(1, 13):
                __write_img_processed(f'{start_year}-{end_year}', month, sum_values[month - 1], data_point)
                pbar.update(1)

def process_humidity():
    Image.MAX_IMAGE_PIXELS = None
    point = 'QV'

    # Write the average values to a TIF file
    with progress(f"Generating images ({point})", 12) as pbar:
        for month in range(1, 13):
            data = __load_data(1981, month, point)
            # Replace invalid values with 0
            # data[data == -999] = 0
            __write_img_processed(f'1981', month, data, point)
            pbar.update(1)