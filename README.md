# Trail-Sense-Earth-Model
A generator for Trail Sense which generates Earth models such as historic temperatures and geoids.

# Using CRU
1. Extract .dat files from https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/ into the source folder
2. Update the Input section of the parse-cru.py script with the dates, datapoint type, and scale of the data (ex. C x 10), run the script
3. Update the Input section of the convert-images-monthly.py script to match the data (ex. tmn, tmx as data_point types and 2 degrees per pixel), run the script
4. Images will appear in the output directory

# Using MERRA-2
1. Add a text file titled "nasa-credentials.txt" to the root directory. The first line is your username, the second line is your password for the NASA GESDISC data server.
2. Update the Input section of the download-merra2.py script to match the data you want to retrieve (ex. T2MMIN, T2MMAX), run the script
3. Download the 60-arc second resolution surface elevation and geoid file from https://www.ncei.noaa.gov/products/etopo-global-relief-model - put in the source/etopo folder
4. Update the Input section of the parse-merra2.py script to match the downloaded data (ex. T2MMIN, T2MMAX), run the script
5. Update the Input section of the convert-images-monthly.py script to match the data (ex. T2MMIN, T2MMAX as data_point types and 2 and 1.6 degrees per pixel for latitude and longitude respectively), run the script
6. Images will appear in the output directory

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

## WorldClim
Fick, S.E. and R.J. Hijmans, 2017. WorldClim 2: new 1km spatial resolution climate surfaces for global land areas. International Journal of Climatology 37 (12): 4302-4315.