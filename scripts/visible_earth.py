import requests
import os
import PIL.Image as Image
import numpy as np
from sklearn.cluster import KMeans
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


def __simplify(reference_image, target_image, colors):
    global kmeans
    if kmeans is None:
        # Convert the reference image to HSV
        reference_image_hsv = reference_image.convert("HSV")
        reference_pixels = np.array(reference_image_hsv)
        reference_pixels_reshaped = reference_pixels.reshape(-1, 3)

        # Apply K-Means clustering to the HSV pixels of the reference image
        kmeans = KMeans(n_clusters=colors, random_state=0)
        kmeans.fit(reference_pixels_reshaped)

    # Convert the target image to HSV
    target_image_hsv = target_image.convert("HSV")
    target_pixels = np.array(target_image_hsv)
    target_pixels_reshaped = target_pixels.reshape(-1, 3)

    # Predict the cluster for each pixel in the target image
    labels = kmeans.predict(target_pixels_reshaped)
    compressed_pixels = kmeans.cluster_centers_[labels]
    compressed_pixels = compressed_pixels.reshape(target_pixels.shape)

    # Ensure values are within valid HSV range
    compressed_pixels = np.clip(compressed_pixels, 0, 255).astype(np.uint8)

    # Convert the HSV image back to RGB
    compressed_image = Image.fromarray(compressed_pixels, "HSV").convert("RGB")

    return compressed_image


def process_maps(colors = 16):
    if not os.path.exists("images"):
        os.makedirs("images")

    reference = Image.open("source/visible-earth/3.jpg")
    with tqdm(total=12, desc="Processing Visible Earth images") as pbar:
        for month in range(1, 13):
            image = Image.open(f"source/visible-earth/{month}.jpg")
            if colors > 0:
                image = __simplify(reference, image, colors)
            image.save(f"images/world-map-{month}.tif")
            pbar.update(1)
