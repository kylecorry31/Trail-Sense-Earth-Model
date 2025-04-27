import cdsapi
import os
from tqdm import tqdm
import xarray as xr
from datetime import datetime
import PIL

source_folder = "source/era5"
images_folder = "images"


def __download(start_year, end_year, variable, dataset):
    # Create the folder if it doesn't exist
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)

    years = [str(i) for i in range(start_year, end_year + 1)]
    c = cdsapi.Client()

    request = {
        "format": "netcdf",
        "product_type": "monthly_averaged_reanalysis",
        "variable": variable.split(","),
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
    }

    if 'pressure-levels' in dataset:
        request["pressure_level"] = "1000"

    c.retrieve(
        dataset,
        request,
        f"{source_folder}/{variable}-{start_year}-{end_year}.nc",
    )


def download(start_year=1991, end_year=2020, redownload=False):

    if not os.path.exists('.cdsapirc'):
        key = input("CDS API key: ")
        with open('.cdsapirc', 'w') as f:
            f.write(f'url: https://cds.climate.copernicus.eu/api\n')
            f.write(f'key: {key}\n')

    with open('.cdsapirc', 'r') as f:
        lines = f.readlines()
    with open(f'/home/vscode/.cdsapirc', 'w') as f:
        for line in lines:
            f.write(line)

    if redownload or not os.path.exists(
        f"{source_folder}/relative_humidity-{start_year}-{end_year}.nc"
    ):
        with tqdm(total=1, desc="Downloading ERA5 Humidity") as pbar:
            __download(start_year, end_year, 'relative_humidity',
                       'reanalysis-era5-pressure-levels-monthly-means')
            pbar.update(1)

    if redownload or not os.path.exists(
        f"{source_folder}/total_precipitation-{start_year}-{end_year}.nc"
    ):
        with tqdm(total=1, desc="Downloading ERA5 Precipitation") as pbar:
            # https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview
            __download(start_year, end_year, 'total_precipitation',
                       'reanalysis-era5-single-levels-monthly-means')
            pbar.update(1)

    if redownload or not os.path.exists(
        f"{source_folder}/type_of_low_vegetation,type_of_high_vegetation-{end_year}-{end_year}.nc"
    ):
        with tqdm(total=1, desc="Downloading ERA5 Vegetation") as pbar:
            # https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=overview
            # Only needs 1 year
            __download(end_year, end_year, 'type_of_low_vegetation,type_of_high_vegetation',
                       'reanalysis-era5-single-levels-monthly-means')
            pbar.update(1)

    # Other useful parameters:
    # Snowfall - sf
    # Leaf area index, low vegetation - lai_lv
    # Leaf area index, high vegetation - lai_hv
    # Surface pressure - sp
    # Mean sea level pressure - msl
    # Total cloud cover - tcc
    # Total totals index - totalx (thunderstorm potential)
    # Type of high vegetation - tvh
    # Type of low vegetation - tvl


def __process_dataset(variable, selector, start_year=1991, end_year=2020, name_override=None):
    # Open the netcdf file
    dataset = xr.open_dataset(
        f"{source_folder}/{variable}-{start_year}-{end_year}.nc"
    )

    # Preload the data into memory
    yearly_data = []
    with tqdm(total=(end_year - start_year + 1) * 12, desc=f"Processing ERA5 {variable}") as pbar:
        for year in range(start_year, end_year + 1):
            monthly_data = []
            for month in range(1, 13):
                values = dataset[selector].sel(
                    valid_time=datetime(year, month, 1, 0, 0, 0), method="nearest"
                ).values

                if len(values) == 1:
                    values = values[0]

                monthly_data.append(values)
                pbar.update(1)
            yearly_data.append(monthly_data)

    def get_value(latitude, longitude, year, month):
        # Convert the longitude to the range 0-360
        if longitude < 0:
            longitude += 360
        return yearly_data[year - start_year][month - 1][
            int((latitude + 90) * 4), int(longitude * 4)
        ]

    def get_average_value(latitude, longitude, month):
        total = 0
        years = range(start_year, end_year + 1)
        for year in years:
            total += get_value(latitude, longitude, year, month)
        return total / len(years)

    # Create a map of the humidity data for a single month (180 x 360)
    scale = 0.25

    if not os.path.exists(images_folder):
        os.mkdir(images_folder)

    width = int(360 / scale)
    height = int(180 / scale)

    with tqdm(desc="Calculating climate normals", total=12 * width * height) as pbar:
        for month in range(1, 13):
            image = PIL.Image.new("F", (width, height))

            for i in range(image.height):
                for j in range(image.width):
                    latitude = i * scale - 90
                    longitude = j * scale - 180
                    humidity_value = get_average_value(
                        latitude, longitude, month)
                    image.putpixel((j, i), humidity_value)
                    pbar.update(1)

            # Save the image as a tif
            image.save(
                f"{images_folder}/{start_year}-{end_year}-{month}-{variable if name_override is None else name_override}.tif")


def process_humidity(start_year=1991, end_year=2020):
    __process_dataset('relative_humidity', 'r', start_year, end_year)


def process_precipitation(start_year=1991, end_year=2020):
    __process_dataset('total_precipitation', 'tp', start_year, end_year)


def process_vegetation(year=2020):
    __process_dataset('type_of_low_vegetation,type_of_high_vegetation',
                      'tvh',  year, year, 'high_vegetation')
    __process_dataset('type_of_low_vegetation,type_of_high_vegetation',
                      'tvl', year, year, 'low_vegetation')
