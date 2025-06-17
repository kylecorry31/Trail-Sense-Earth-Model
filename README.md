# Trail-Sense-Earth-Model
A generator for Trail Sense which generates Earth models such as historic temperatures and geoids.

**generate-temperature-model.py**: The script to generate the global temperature model. This will generate 8 WEBP files in the output directory for the min/max monthly temperatures. Resolution is 576x361.

**generate-humidity-model.py**: The script to generate the global humidity model. This will generate 4 WEBP files in the output directory for the monthly humidity. Resolution is 576x361.

**generate-precipitation-model.py**: The script to generate the global precipitation model. This will generate 4 WEBP files in the output directory for the monthly precipitation (monthly total). Resolution is 576x361.

**generate-vegetation-model.py**: The script to generate the global vegetation model. This will generate 1 WEBP file in the output directory for the vegetation types from ERA5. Resolution is 576x361.

**generate-geoid-model.py**: The script to generate the geoid model. This will generate 1 WEBP file in the output directory. Resolution is 361x181.

**generate-tide-model.py**: The script to generate the tide model. This will generate 1 WEBP file for each tidal constituent (currently 17 files) with the red channel being the amplitude (normalized between 0 and 1 and with the 4th root taken on the normalized data) and the green channel being the phase (noramlized between 0 and 1, source is betwen -180 and 180). It will output the max amplitude for each constituent (scale is 0 to max amplitude in cm). Resolution is 720x360.

**generate-tide-corrections.py**: The script to generate the astronomical tide corrections. It will output the corrections for each tide constituent.

**generate-star-model.py**: The script to generate the star model. It will output the Kotlin enums for the specified list of stars.

**generate-timezone-location-map.py**: The script to generate coordinates for each timezone ID.

**generate-species-catalog.py**: The script to generate a species catalog of the most common species. It will output JSON files to output/species-catalog.

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

# timezonefinder
The MIT License (MIT)
Copyright (c) 2016 Evan Siroky

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# iNaturalist
Used to get the most common species.

https://www.inaturalist.org/pages/api+reference

# Wikipedia
Species catalog information.

https://en.wikipedia.org/api/rest_v1

https://en.wikipedia.org (see the wikipedia link in each species catalog notes section)

# OpenCelliD
OpenCelliD Project is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License

https://opencellid.org/

# SRTM
NASA Shuttle Radar Topography Mission, public domain
https://data.noaa.gov/onestop/collections/details/96d77f2d-1ec2-4967-baa0-89626dc803bf