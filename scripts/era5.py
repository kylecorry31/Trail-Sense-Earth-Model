import cdsapi
import os
from tqdm import tqdm
import xarray as xr
from datetime import datetime
import PIL

source_folder = "source/era5"
images_folder = "images"


def __download(start_year, end_year):
    # Create the folder if it doesn't exist
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)

    years = [str(i) for i in range(start_year, end_year + 1)]
    c = cdsapi.Client()

    c.retrieve(
        "reanalysis-era5-pressure-levels-monthly-means",
        {
            "format": "netcdf",
            "product_type": "monthly_averaged_reanalysis",
            "variable": "relative_humidity",
            "pressure_level": "1000",
            "year": years,
            "month": [
                "01",
                "02",
                "03",
                "04",
                "05",
                "06",
                "07",
                "08",
                "09",
                "10",
                "11",
                "12",
            ],
            "time": "00:00",
        },
        f"{source_folder}/humidity-{start_year}-{end_year}.nc",
    )


def download(start_year=1991, end_year=2020, redownload=False):
    if not redownload and os.path.exists(
        f"{source_folder}/humidity-{start_year}-{end_year}.nc"
    ):
        return

    with tqdm(total=1, desc="Downloading ERA5") as pbar:
        __download(start_year, end_year)
        pbar.update(1)


def process_humidity(start_year=1991, end_year=2020):
    # Open the netcdf file
    humidity = xr.open_dataset(
        f"{source_folder}/humidity-{start_year}-{end_year}.nc"
    )

    # Preload the data into memory
    yearly_data = []
    for year in range(start_year, end_year + 1):
        monthly_data = []
        for month in range(1, 13):
            humidity_data = humidity.r.sel(
                time=datetime(year, month, 1, 0, 0, 0), method="nearest"
            ).values
            monthly_data.append(humidity_data)
        yearly_data.append(monthly_data)

    def get_humidity(latitude, longitude, year, month):
        # Convert the longitude to the range 0-360
        if longitude < 0:
            longitude += 360
        return yearly_data[year - start_year][month - 1][
            int((latitude + 90) * 4), int(longitude * 4)
        ]

    def get_average_humidity(latitude, longitude, month):
        total = 0
        years = range(start_year, end_year + 1)
        for year in years:
            total += get_humidity(latitude, longitude, year, month)
        return total / len(years)

    # Create a map of the humidity data for a single month (180 x 360)
    scale = 0.25

    if not os.path.exists(images_folder):
        os.mkdir(images_folder)

    with tqdm(desc="Calculating climate normals", total=12) as pbar:
        for month in range(1, 13):
            image = PIL.Image.new("F", (int(360 / scale), int(180 / scale)))

            for i in range(image.height):
                for j in range(image.width):
                    latitude = i * scale - 90
                    longitude = j * scale - 180
                    humidity_value = get_average_humidity(latitude, longitude, month)
                    image.putpixel((j, i), humidity_value)

            # Save the image as a tif
            image.save(f"{images_folder}/{start_year}-{end_year}-{month}-humidity.tif")
            pbar.update(1)
