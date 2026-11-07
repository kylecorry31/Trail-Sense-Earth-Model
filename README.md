# Trail-Sense-Earth-Model
A generator for Trail Sense which generates Earth models such as historic temperatures and geoids.

## Models

### Temperature
Generated with generate-temperature-model.py.

The temperature model is generated using the MERRA-2 reanalysis data (the 1991 - 2020 climate normal). It is generated using the following steps, separately for the monthly highs (T2MMAX) and lows (T2MMIN):
1. Download the T2MMIN and T2MMAX variables from the MERRA-2 reanalysis data.
2. Calculate the monthly climate averages of each variable, converted to sea level using the ETOPO DEM.
3. Perform harmonic analysis on the 12 monthly averages to get the annual cycle of every cell: the mean, plus the cosine and sine of each of the first 4 harmonics.
4. Fit a polynomial of the sine of latitude (degree 4, weighted by the area of each row) to the mean image and subtract it, which narrows the range of the mean. The coefficients of the polynomial are stored in the app.
5. Stretch each image to 8 bits using a linear stretch (value = pixel / a - b), with the coefficients stored in the app.
6. Save each image as a lossy WEBP. Each image is encoded at a range of qualities, and the quality of each is chosen to get the lowest area-weighted error within the size budget. The mean counts twice as much as each harmonic image in the error, since it applies to every month. In practice, this leads to the lower harmonics being encoded at lower quality since they contribute less to the overall error.

To get the temperature in a month, the app reads the 9 values at the location, reverses the stretch, adds the latitude polynomial back to the mean, sums the harmonics for the month, and adjusts the sea level temperature to the elevation at the location.

The test data for the model can be generated with generate-temperature-test-data.py.

### Precipitation
Generated with generate-precipitation-model.py.

The precipitation model is generated using the ERA5 monthly averaged reanalysis data (the 1991 - 2020 climate normal). It is generated using the following steps:
1. Download the total precipitation variable from ERA5 for every year of the normal.
2. Calculate the climate average of each month and convert it to the monthly total in mm.
3. Average the source pixels down to the model resolution.
4. Take the square root of each monthly total. This keeps the error proportional to the amount of precipitation, so dry places keep their detail and wet places don't waste bits.
5. Stretch the square root linearly to 8 bits.
6. Save each month as a lossy WEBP.

To get the precipitation in a month, the app reads the pixel of that month at the location and reverses the stretch (mm = (pixel / a - b)^2).

The test data for the model can be generated with generate-precipitation-test-data.py.

### Tides
Generated with generate-tide-model.py.

The tide model is generated using the EOT20 ocean tide model, which gives the amplitude and phase of each tidal constituent. It is generated using the following steps:
1. Download EOT20 and the Natural Earth land data.
2. Load the amplitude and phase of each constituent as a phasor (x, y), so cells can be averaged. Invalid cells (land) are masked using Natural Earth, keeping the ocean around islands smaller than a pixel.
3. Split the globe into cells using a quadtree. Cells start at 1 degree and are split in half, down to 0.25 degrees, wherever the tide varies more between neighbors. The split with the most to gain is made first until the cell budget is used (the budget sets the size of the model).
4. Set each cell to the phasor average of the valid source cells it covers, so coastal cells are kept even when only some of their source cells have data.
5. Order the cells along a Hilbert curve so neighboring cells are next to each other, and replace the values of a cell with a neighbor's wherever that changes the tide at the cell by less than 1%. Both make the model compress better.
6. Convert back to an amplitude and phase. Amplitudes too large to store are removed from the images and listed separately (as constituent, row, column, and amplitude in cm). The rest are normalized to 0 to 1 by the max amplitude of each constituent.
7. Stretch the amplitudes and phases to 8 bits and save them as lossless WEBPs with 3 constituents per file. Also save an index image which maps each pixel to its cell in those files.

To get the tide at a location, the app looks up the cell of the location in the index image, reads the amplitude and phase of each constituent for that cell (reversing the normalization), and sums the constituents at the time of interest.

The generate-tide-prediction-constants.py script fetches the lunitidal interval and harmonic constituents of a NOAA station, for testing the model.

### Elevation
Generated with generate-dem.py.

The elevation model is generated using ETOPO 2022. It is generated using the following steps:
1. Download the ETOPO 2022 tiles (15 x 15 degrees) and the source identifier tiles.
2. Remove the ocean and bathymetry by masking the pixels that the source identifier image does not mark as land or lake. Inland water is masked separately, so it can be kept apart from the ocean.
3. Skip tiles which are all ocean.
4. Resize each tile (averaging the source pixels) and save it according to the size:
   - **High**: 16-bit lossless (split across two channels) with a water mask channel (ocean, inland water, or land).
   - **Medium**: stretched to 8 bits, at the source resolution.
   - **Low** and **Mini**: stretched to 8 bits, lossy. The resolution and WebP quality of each tile is chosen to get the lowest error within a size budget. Every tile is saved at a range of resolutions and qualities, and the option for each tile that has the lowest total cost, while fitting in the budget, is chosen. The cost of an option is its mean absolute error plus its loss of detail (the elevation changes between nearby points that make up the gain of a route), weighted by the ground area of the tile, its relief, and its latitude.
5. **Mini** and **low** also save the summits the model flattens the most to peaks.tsgeo (see below), up to a size budget (256 KB for mini and 512 KB for low). A summit is the highest pixel within about 5 km that is at least 300 m above its surroundings. It is kept if the model is at least 110 m below it and already rises toward it by at least half that amount.
6. Write an index (index.json) with the stretch coefficients, bounds, and size of each tile, and zip the result.

To get the elevation at a location, the app reads the tile that contains it, interpolates the pixels around the location, and reverses the stretch. If the model has a peaks.tsgeo, the app also raises the model around nearby summits.

**peaks.tsgeo** is a [geo point file](docs/geo-point-file-format.md):

| Setting | Value |
| --- | --- |
| `cell_degrees` | 5 |
| `decimals` | 3 |
| `scale` field | 1 byte, step 1/64 |
| `base` field | 2 bytes, step 16 m |
| `properties` | `{"type": "peaks", "radius_meters": 4000}` |

The base is the average elevation of the model `radius_meters` (R) from the summit, and the scale makes the model reach the summit. At a distance d from a summit, where the model is at an elevation e, the app adds `scale * max(e - base, 0) * (1 - (d / R)^2)^2`, summed over the nearby summits. A point of a grid is raised by at least as much as the highest summit within the area it covers (with d measured from the nearest edge of that area), so summits keep their height on coarse grids.

The test data for the model can be generated with generate-dem-test-data.py.

### Stars
Generated with generate-star-model.py.

The star model is generated using the SIMBAD astronomical database and the IAU star names and constellation lines. It is generated using the following steps:
1. Query SIMBAD for all stars brighter than a magnitude cutoff, plus the stars needed for the constellation lines and a few additional stars.
2. Remove components of a star that has a parent object (ex. Alpha Crucis A when Alpha Crucis exists), and a few ignored stars.
3. Get the details of each star: Hipparcos ID, the IAU proper name (or the Bayer designation if it has none), coordinates, magnitude, proper motion, and color index.
4. Map the constellation lines to the Hipparcos IDs of the stars.
5. Output the stars and constellations as Kotlin code (output/stars.kt and output/constellations.kt).

To get the position of a star, the app applies the proper motion to the coordinates and converts them to the horizon at the location and time.

### Timezones
Generated with generate-timezone-location-map.py.

The timezone model is a coordinate for each timezone ID, which the app uses to find the closest timezone to a location. It is generated using the following steps:
1. Get the boundary geometry of each timezone from timezonefinder.
2. Skip the timezones that are not in a region (ex. Etc/GMT+1).
3. Find the extent of the boundary (accounting for boundaries that cross the antimeridian) and use its center as the coordinate of the timezone.
4. Output the timezone IDs and coordinates (rounded to whole degrees) as a Kotlin array.

### Cell Towers
Generated with generate-cell-tower-model.py.

The cell tower model is a map of where cell service is likely to be available. It is generated using the following steps:
1. Download the FCC antenna registrations, OpenCelliD, and Mozilla Location Service (MLS) data.
2. Remove towers which are likely outdated or inaccurate: those not updated in the past 5 years, and those with fewer than 3 samples (unless they are not changeable). Towers are deduplicated by network, country, and area, preferring the unchangeable entry and then the one with the most samples.
3. Merge the towers into a grid of 0.01 degrees (about 1 km): each square that has a tower is stored once, at its position rounded to 2 decimal places (about 1 km).

**cell_towers.tsgeo** is a [geo point file](docs/geo-point-file-format.md):

| Setting | Value |
| --- | --- |
| `cell_degrees` | 5 |
| `decimals` | 2 |
| fields | none |
| `properties` | `{"type": "cell_towers"}` |

To check for service at a location, the app reads the towers near it from cell_towers.tsgeo and checks whether one is in range.

### Magnetic Field
Generated with generate-magnetic-field-model.py.

The magnetic field model is the World Magnetic Model (WMM) from NOAA. It is generated using the following steps:
1. Download the WMM coefficients file (WMM.COF).
2. Parse the Gauss coefficients (g and h) and their yearly rates of change (delta g and delta h) for each degree and order.
3. Output them as Java arrays.

To get the magnetic declination at a location, the app calculates the field from the spherical harmonic expansion of the coefficients, advanced to the date of interest using the yearly rates.

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
