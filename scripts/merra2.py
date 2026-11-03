import PIL.Image as Image
import numpy as np
import os
from pydap.client import open_url
from scripts import to_tif, load_pixels
from scripts.progress import progress
import earthaccess

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

def __get_cell_mean_elevations(elevations, height, width):
    """
    The mean elevation of the area each grid point stands for. The temperature of a point is the mean of its whole cell
    (0.5 degrees by 0.625 degrees, centered on the point), so it is reduced to sea level with the mean elevation of the
    cell rather than the elevation at the point, which is up to thousands of meters different in the mountains.
    """
    rows, columns = elevations.shape
    elevations = np.where(elevations == elevation_invalid_value, 0, elevations).astype(np.float64)
    cell_height = 180 / (height - 1)
    cell_width = 360 / width
    means = np.zeros((height, width))
    for y in range(height):
        latitude = 90 - y * cell_height
        top = int(np.floor((90 - min(latitude + cell_height / 2, 90)) / 180 * rows))
        bottom = max(int(np.ceil((90 - max(latitude - cell_height / 2, -90)) / 180 * rows)), top + 1)
        row = elevations[top:bottom].mean(axis=0)
        # Cumulative sums around the antimeridian
        padded = np.concatenate([[0], np.cumsum(np.concatenate([row, row]))])
        for x in range(width):
            longitude = -180 + x * cell_width
            first = int(np.floor((longitude - cell_width / 2 + 180) / 360 * columns))
            last = int(np.ceil((longitude + cell_width / 2 + 180) / 360 * columns))
            count = max(last - first, 1)
            start = first % columns
            means[y, x] = (padded[start + count] - padded[start]) / count
    return means

def __to_sea_level(data, elevations):
    # Invert elevation to bring it back down to sea level
    return data + 0.0065 * elevations

def __load_data(year, month, data_point):
    return load_pixels(f'source/merra2/{year}-{month}-{data_point}.tif')

def __write_img_processed(year, month, values, data_point):
    to_tif(values, f'images/{year}-{month}-{data_point}.tif')

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



def process_temperatures(start_year=1991, end_year=2020):
    data_points = ['T2MMIN', 'T2MMAX']
    Image.MAX_IMAGE_PIXELS = None
    with progress("Loading elevation data", 1) as pbar:
        elevations = load_pixels(elevation_image)
        height, width = __load_data(start_year, 1, data_points[0]).shape
        elevations = __get_cell_mean_elevations(elevations, height, width)
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