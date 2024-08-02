# Trail-Sense-Earth-Model
A generator for Trail Sense which generates Earth models such as historic temperatures and geoids.

**generate-temperature-model.py**: The script to generate the global temperature model. This will generate 8 WEBP files in the output directory for the min/max monthly temperatures. Resolution is 576x361.

**generate-humidity-model.py**: The script to generate the global humidity model. This will generate 4 WEBP files in the output directory for the monthly humidity. Resolution is 576x361.

**generate-geoid-model.py**: The script to generate the geoid model. This will generate 1 WEBP file in the output directory. Resolution is 361x181.

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

## Uptide
Licensed under LGPL-3.0: https://github.com/stephankramer/uptide/blob/master/LICENSE