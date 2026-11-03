# Trail-Sense-Earth-Model
A generator for Trail Sense which generates Earth models such as historic temperatures and geoids.

**generate-temperature-model.py**: The script to generate the global temperature model. This will generate 18 WEBP files in the output directory (9 for the monthly highs and 9 for the monthly lows). Each quantity is stored as an annual cycle (the mean and 4 harmonics) at sea level, with a polynomial of sin(latitude) removed from the mean, and the elevation of each 0.5 x 0.625 degree cell is the average of the ETOPO elevations in it. The quality of each image is chosen to fit a size budget. Resolution is 576x361.

**generate-temperature-test-data.py**: Generates the test data for the temperature model (the full precision sea level monthly highs and lows at the 100 points of the precipitation test data).

**generate-dewpoint-model.py**: The script to generate the global dewpoint model. This will generate 4 WEBP files in the output directory for the monthly dewpoint. Resolution is 360x180.

**generate-precipitation-model.py**: The script to generate the global precipitation model. This will generate 12 WEBP files in the output directory for the monthly precipitation (monthly total in mm, as 8-bit values where mm = (pixel / 4.4)^2). Resolution is 1440x720. The square root keeps the error proportional to the amount of precipitation, and the lossy WebP quality (encoded with `cwebp`) sets the size of the model.

**generate-vegetation-model.py**: The script to generate the global vegetation model. This will generate 1 WEBP file in the output directory for the vegetation types from ERA5. Resolution is 576x361.

**generate-worldcover-map.py**: The script to generate the global worldcover map. This will generate 1 WEBP file in the output directory for worldcover. Resolution is 3800x1900.

**generate-geoid-model.py**: The script to generate the geoid model. This will generate 1 WEBP file in the output directory. Resolution is 361x181.

**generate-dem.py**: The script to generate the digital elevation models (DEM) from ETOPO 2022, as 15 degree tiles in 4 sizes: high (16-bit lossless, with a water mask), medium (8-bit, quality 100), low, and mini (the built-in model). Low and mini choose the resolution and WebP quality of each tile to get the lowest error within a size budget. Every tile is saved at a range of resolutions (averaging the source pixels) and qualities, and elevations are rounded to 8 bits. The option for each tile that has the lowest total cost, while fitting in the budget, is chosen. The cost of an option is its mean absolute error against the source plus its loss of detail (the elevation changes between nearby points that make up the gain of a route), weighted by the ground area the tile covers (tiles are also narrower towards the poles to match), how much relief it has (errors matter more in rugged terrain), and its latitude (errors matter less in the arctic). It outputs a zip file for each size to the output directory. Requires `cwebp` (the `webp` package), which is used to encode the tiles without the adaptive quantization that makes smooth terrain blocky.

**generate-dem-test-data.py**: The script to generate the reference data used to test the DEMs in Trail Sense. It will output CSV files with random points in hiking areas (grouped by mountains, hills, and flat terrain) plus a few over the ocean and well known peaks, points along hiking routes (for elevation gain and loss), and pairs of points on either side of a tile boundary (and a control set of the same size away from any boundary). The reference elevations are from the Copernicus DEM (via open-meteo), except for the peaks, which use their official elevation.

**generate-precipitation-test-data.py**: The script to generate the reference data used to test the precipitation model in Trail Sense. It will output a CSV file with the full resolution ERA5 monthly precipitation (mm) at 100 points: 60 random hiking area points from the DEM test data (run generate-dem-test-data.py first) and 40 random points over the land of the world.

**generate-tide-model.py**: The script to generate the tide model. This will generate WEBP files in the output directory for the amplitude (normalized between 0 and 1, 3 constituents per file) and phase (normalized between 0 and 1, source is between -180 and 180) of each tidal constituent (currently 17), plus an index image (1440x720) which maps each pixel to its cell in those files. Cells are 1 degree, split in half down to 0.25 degrees where the tide varies more between neighbors (up to the cell budget, which sets the size of the model), and each cell is the phasor average of the valid 0.125 degree source cells it covers, so coastal cells are kept even when only some of their source cells have data. Cells are ordered along a Hilbert curve, and values are replaced by a neighbor's wherever that changes the tide at the cell by less than 1%, both of which make the model compress better. It will output the max amplitude for each constituent (scale is 0 to max amplitude in cm) and the cells with amplitudes too large to store (as row, column, amplitude in cm, where row and column are the position of the cell in the amplitude files).


**generate-star-model.py**: The script to generate the star model. It will output the Kotlin enums for the specified list of stars.

**generate-timezone-location-map.py**: The script to generate coordinates for each timezone ID.

**generate-cell-tower-model.py**: The script to generate a cell tower model. It will output a SQLLite DB to output/cell_towers.db.

**generate-magnetic-field-model.py**: The script to generate the World Magnetic Model coefficients. It will output the WMM coefficients as Java arrays into the console.

# Credits
## CRU
Climatic Research Unit (University of East Anglia) and Met Office (https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/). Listed under the Open Government Licence: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/

## MERRA-2
Global Modeling and Assimilation Office (GMAO) (2015), MERRA-2 statM_2d_slv_Nx: 2d,Monthly,Aggregated Statistics,Single-Level,Assimilation,Single-Level Diagnostics V5.12.4, Greenbelt, MD, USA, Goddard Earth Sciences Data and Information Services Center (GES DISC), Accessed: 2023-05-22, 10.5067/KVIMOMCUO83U

## ETOPO 2022
NOAA National Centers for Environmental Information. 2022: ETOPO 2022 15 Arc-Second
Global Relief Model. NOAA National Centers for Environmental Information.
https://doi.org/10.25921/fd45-gt74 . Accessed 2023-05-26.
ETOPO 2022 metadata may be accessed here: ETOPO 2022 metadata landing page

## Natural Earth (for land masking)
Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com.

## ERA5
Contains modified Copernicus Climate Change Service information 1991 - 2020. Neither the European Commission nor ECMWF is responsible for any use that may be made of the Copernicus information or data it contains.

Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2023): ERA5 monthly averaged data on pressure levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.6860a573 (Accessed on 17-NOV-2023)

## Visible Earth
R. Stockli, E. Vermote, N. Saleous, R. Simmon and D. Herring (2005). The Blue
Marble Next Generation - A true color earth dataset including seasonal dynamics
from MODIS. Published by the NASA Earth Observatory. Corresponding author:
rstockli@climate.gsfc.nasa.gov

## ESA WorldCover
© ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data
(2021) processed by ESA WorldCover consortium.

Zanaga, D., Van De Kerchove, R., Daems, D., et al. (2022). ESA WorldCover 10 m
2021 v200. https://doi.org/10.5281/zenodo.7254221

https://esa-worldcover.org/en/data-access

## Copernicus DEM (test data only)
Reference elevations for testing the DEM were generated using Copernicus DEM data via https://open-meteo.com.

ESA - Users, who, in their research, use the Copernicus DEM, are requested to use the following DOI when citing the data source in their publications: https://doi.org/10.5270/ESA-c5d3d65

## pyTMD
https://github.com/tsutterley/pyTMD

MIT License, Copyright (c) 2017 Tyler C Sutterley

## NOAA
NOAA CO-OPS API: https://api.tidesandcurrents.noaa.gov/mdapi/prod/ and https://api.tidesandcurrents.noaa.gov/api/prod/

WMM: https://www.ncei.noaa.gov/products/world-magnetic-model/wmm-coefficients

## EOT20
https://creativecommons.org/licenses/by/4.0/

Hart-Davis Michael, Piccioni Gaia, Dettmering Denise, Schwatke Christian, Passaro Marcello, Seitz Florian (2021). EOT20 - A global Empirical Ocean Tide model from multi-mission satellite altimetry. SEANOE. https://doi.org/10.17882/79489

## SIMBAD
https://doi.org/10.1051/aas:2000332

This research has made use of the SIMBAD database, operated at CDS, Strasbourg, France. 2000,A&AS,143,9 , "The SIMBAD astronomical database", Wenger et al.

## timezonefinder
The MIT License (MIT)
Copyright (c) 2016 Evan Siroky

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## OpenCelliD
OpenCelliD Project is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License

https://opencellid.org/

## FCC
Public domain antenna registrations

https://www.fcc.gov/uls/transactions/daily-weekly

## Mozilla Location Service (MLS)
Public domain, final cell tower export. By Mozilla Corporation. Discontinued in 2024.

https://archive.org/details/MLS_Full_Cell_Export_Final
