import requests
import os
import gzip
import shutil
from scripts.progress import progress

api_key_file = 'opencellid-api-key.txt'
source_folder = 'source/opencellid'
images_folder = 'images/opencellid'
csv_path = f'{source_folder}/cell_towers.csv'


# TODO: Keep older versions of the opencellid dataset and merge it into the new one
def download(redownload=False):
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)

    if not redownload and os.path.exists(f'{source_folder}/cell_towers.csv'):
        return

    if not os.path.exists(api_key_file):
        api_key = input("OpenCellID API key: ")
        with open(api_key_file, 'w') as f:
            f.write(api_key)
    else:
        with open(api_key_file, 'r') as f:
            api_key = f.read().strip()
    with progress("Downloading and unzipping data", 1) as pbar:
        url = f'https://opencellid.org/ocid/downloads?token={
            api_key}&type=full&file=cell_towers.csv.gz'
        r = requests.get(url)
        with open(f'{source_folder}/cell_towers.csv.gz', 'wb') as f:
            f.write(r.content)

        pbar.update(1)

        # Unzip the file
        with gzip.open(f'{source_folder}/cell_towers.csv.gz', 'rb') as f_in:
            with open(f'{source_folder}/cell_towers.csv', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        os.remove(f'{source_folder}/cell_towers.csv.gz')

        pbar.update(1)