import PIL.Image as Image
import os
from pydap.client import open_url
from pydap.cas.urs import setup_session

# Input
start_year = 1991
end_year = 2020
data_point = 'T2MMIN'
offset = -273.15

############ Program, don't modify ############
with open('nasa-credentials.txt', 'r') as f:
    username = f.readline().strip()
    password = f.readline().strip()

def get_version(year, month):
    if year == 2020 and month == 9:
        return 401

    if year <= 1991:
        return 100
    elif year < 2001:
        return 200
    elif year < 2011:
        return 300
    else:
        return 400


def get_data(year, month):
    version = get_version(year, month)
    dataset_url = f'https://goldsmr4.gesdisc.eosdis.nasa.gov/opendap/MERRA2_MONTHLY/M2SMNXSLV.5.12.4/{year}/MERRA2_{version}.statM_2d_slv_Nx.{year}{str(month).zfill(2)}.nc4?{data_point}'
    session = setup_session(username, password, check_url=dataset_url)
    data = open_url(dataset_url, session=session)
    session.close()
    values = data[data_point][0, :, :][0]
    values = [[float(x) + offset for x in value] for value in values]
    return values

def write_img(year, month, values):
    img = Image.new('F', (len(values[0]), len(values)), color='black')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            t = values[y][x]
            pixels[x, img.size[1] - y - 1] = t
    if not os.path.exists('nasa-images'):
        os.mkdir('nasa-images')
    img.save(f'nasa-images/{year}-{month}-{data_point}.tif')

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        print(f'Processing {year}-{month}')
        values = get_data(year, month)
        write_img(year, month, values)