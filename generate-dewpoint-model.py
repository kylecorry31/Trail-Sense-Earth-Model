from scripts import era5, etopo, natural_earth
from scripts.files import monthly_files
from scripts.report import print_stretch
from scripts.operators import (
    process,
    Replace,
    Offset,
    AdjustForElevation,
    Stretch,
    LinearCompression,
    Resize,
    Save,
)

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

# INPUT
start_year = 1991
end_year = 2020

######## Program, don't modify ########
era5.download(start_year, end_year)
etopo.download()
natural_earth.download()

etopo.process_dem()
era5.process_dew_point(start_year, end_year)

elevations, _ = process(
    [etopo.dem_land_path],
    Replace(etopo.elevation_invalid_value),
)

_, results = process(
    monthly_files(start_year, end_year, "2m_dewpoint_temperature"),
    # Kelvin to Celsius (offset 272.15), then to sea level (the dew point drops 1 degree per km of elevation)
    Offset(-272.15),
    AdjustForElevation(elevations[0], 0.001),
    Replace(-999, 0),
    Stretch(),
    Resize((360, 180)),
    Save(
        "output/dewpoint/dewpoint-{range}.webp",
        group=3,
        quality=100,
        lossless=False,
    ),
)

# Every month is stretched the same
print_stretch("dewpoint", results.of(LinearCompression)["coefficients"][:1])
