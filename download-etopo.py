import os
import requests

grid = 60
redownload = True

############ Program, don't modify ############

def get_url(latitude, longitude, data_type, type_path=None):
    lat = ('N' if latitude >= 0 else 'S') + str(abs(latitude)).zfill(2)
    lon = ('E' if longitude >= 0 else 'W') + str(abs(longitude)).zfill(3)
    url = f'https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/{grid}s/{grid}s_{data_type if type_path is None else type_path}_gtif/ETOPO_2022_v1_{grid}s_{lat}{lon}_{data_type}.tif'
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

download(get_url(90, -180, 'geoid'))
download(get_url(90, -180, 'surface'))