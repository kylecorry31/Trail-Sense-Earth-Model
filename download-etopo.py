import os
import requests

grid = 15
redownload = False

############ Program, don't modify ############

def get_url(latitude, longitude, type_path, type):
    lat = ('N' if latitude >= 0 else 'S') + str(abs(latitude)).zfill(2)
    lon = ('E' if longitude >= 0 else 'W') + str(abs(longitude)).zfill(3)
    url = f'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/{grid}s/{grid}s_{type_path}_gtif/ETOPO_2022_v1_{grid}s_{lat}{lon}_{type}.tif'
    return url

def download(url):
    filename = url.split('/')[-1]
    if not os.path.exists(f'source/etopo'):
        os.makedirs(f'source/etopo')
    if not os.path.exists(f'source/etopo/{filename}') or redownload:
        print(f'Downloading {url}')
        r = requests.get(url)
        if r.status_code == 200:
            with open(f'source/etopo/{filename}', 'wb') as f:
                f.write(r.content)
        else:
            raise Exception(f'Error {r.status_code} downloading {url}')

def download_tiles(type_path, type):
    for lat in range(90, -90, -grid):
        for lon in range(-180, 180, grid):
            url = get_url(lat, lon, type_path, type)
            download(url)

download_tiles('surface_elev', 'surface')
download_tiles('geoid', 'geoid')
download_tiles('surface_sid', 'surface_sid')