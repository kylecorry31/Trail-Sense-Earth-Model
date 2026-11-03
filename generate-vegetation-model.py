from scripts import era5
from scripts.operators import process, Resize, Save, Replace

# Follow these instructions to sign in: https://cds.climate.copernicus.eu/how-to-api#install-the-cds-api-client

start_year = 1991
end_year = 2020

era5.download(start_year, end_year)
era5.process_vegetation(end_year)

process(
    [
        f"images/{end_year}-{end_year}-7-high_vegetation.tif",
        f"images/{end_year}-{end_year}-7-low_vegetation.tif",
    ],
    Replace(-999, 0),
    Resize((576, 361), exact=True),
    Save(["output/vegetation.webp"], group=2, quality=100, lossless=True),
)
