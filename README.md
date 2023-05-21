# Trail-Sense-Temperature-Model
A temperature model generator for Trail Sense.

# How to run
1. Extract .dat files from https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/ into the datfiles folder
2. Update the Input section of the dat-parser.py script with the dates, datapoint type, and whether to generate images (for each year/month)
2. Run the resize_high_low.py to generate the high and low temperature files
3. Run the compress.py script, setting the name of the file to compress
4. Copy the output .txt files into Trail Sense

# Credits
Dataset is from Climatic Research Unit (University of East Anglia) and Met Office (https://crudata.uea.ac.uk/cru/data/hrg/cru_ts_4.07/). Listed under the Open Government Licence: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
