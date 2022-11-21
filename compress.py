import struct

# The input data should be a list of numbers for lat lng values (ordered lat, lng both ascending)
# The data transform can be used for csv files
# The output will be either the byte values for the locations or the count, value if compress is on
# This is a work in progress

compress = False
# inputFile = 'temperatures.csv'
# outputFile = 'temperatures.txt'
# inputFile = 'average_temperature_range.csv'
# outputFile = 'average_temperature_range.txt'
# inputFile = 'temperature_range.csv'
# outputFile = 'temperature_range.txt'
inputFile = 'vapor_pressures.csv'
outputFile = 'vapor_pressures.txt'
compress_format = '>B'
value_format = '>h'
max_compress = 0xff

f = open(inputFile, 'r')
text = f.read().splitlines()
f.close()

data = [round(float(x)) for x in text]

if compress:
    compressed_data = []
    last = None
    for d in data:
        if last is not None and last[1] == d and last[0] < max_compress:
            last = (last[0] + 1, last[1])
        elif last is None:
            last = (1, d)
        else:
            compressed_data.append(last)
            last = (1, d)
    compressed_data.append(last)
    f = open(outputFile, 'wb')
    f.write(b''.join(list(map(lambda x: struct.pack(
        compress_format, x[0]) + struct.pack(value_format, x[1]), compressed_data))))
    f.close()
else:
    f = open(outputFile, 'wb')
    f.write(b''.join(list(map(lambda x: struct.pack(value_format, x), data))))
    f.close()

# TODO: Add decompression