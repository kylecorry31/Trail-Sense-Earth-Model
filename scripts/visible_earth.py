import requests
import os
import PIL.Image as Image
from .progress import progress
from tqdm import tqdm

kmeans = None


def __download(url, filename):
    if not os.path.exists(f"source/visible-earth"):
        os.makedirs(f"source/visible-earth")
    if not os.path.exists(f"source/visible-earth/{filename}"):
        r = requests.get(url)
        if r.status_code == 200:
            with open(f"source/visible-earth/{filename}", "wb") as f:
                f.write(r.content)
        else:
            raise Exception(f"Error {r.status_code} downloading {url}")


def download():
    files = [
        # January
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74243/world.topo.200401.3x5400x2700.jpg",
        # February
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74268/world.topo.200402.3x5400x2700.jpg",
        # March
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74293/world.topo.200403.3x5400x2700.jpg",
        # April
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74318/world.topo.200404.3x5400x2700.jpg",
        # May
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74343/world.topo.200405.3x5400x2700.jpg",
        # June
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74368/world.topo.200406.3x5400x2700.jpg",
        # July
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74393/world.topo.200407.3x5400x2700.jpg",
        # August
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74418/world.topo.200408.3x5400x2700.jpg",
        # September
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74443/world.topo.200409.3x5400x2700.jpg",
        # October
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74468/world.topo.200410.3x5400x2700.jpg",
        # November
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74493/world.topo.200411.3x5400x2700.jpg",
        # December
        "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74518/world.topo.200412.3x5400x2700.jpg",
    ]

    with progress("Downloading Visible Earth images", len(files)) as pbar:
        for i, file in enumerate(files):
            __download(file, f"{i+1}.jpg")
            pbar.update(1)


def process_maps():
    if not os.path.exists("images"):
        os.makedirs("images")

    with tqdm(total=12, desc="Processing Visible Earth images") as pbar:
        for month in range(1, 13):
            image = Image.open(f"source/visible-earth/{month}.jpg")
            image.save(f"images/world-map-{month}.tif")
            pbar.update(1)
