# The input data should be a list of numbers for lat lng values (ordered lat, lng both ascending)
# The data transform can be used for csv files
# The output will be either the byte values for the locations or the count, value if compress is on
# This is a work in progress

name = 'tdelta'
inputFile = f'{name}.csv'
outputFile = f'{name}.txt'



f = open(inputFile, 'r')
text = f.read().splitlines()
f.close()

data = [round(float(x)) for x in text]

def count_bits(n):
    if n == 0:
        return 1

    bits = 0
    while n > 0:
        bits += 1
        n >>= 1

    return bits

def pack_values(values, num_bits):
    packed_bytes = bytearray()
    current_byte = 0
    bits_written = 0

    for value in values:
        value &= (1 << num_bits) - 1  # Apply the mask to extract the desired bits
        bits_needed = num_bits

        while bits_needed > 0:
            bits_to_write = min(bits_needed, 8 - bits_written)
            bits_shift = bits_needed - bits_to_write
            current_byte <<= bits_to_write
            current_byte |= (value >> bits_shift) & ((1 << bits_to_write) - 1)
            bits_needed -= bits_to_write
            bits_written += bits_to_write

            if bits_written == 8:
                packed_bytes.append(current_byte)
                current_byte = 0
                bits_written = 0

    if bits_written > 0:
        current_byte <<= (8 - bits_written)
        packed_bytes.append(current_byte)

    return packed_bytes

def unpack_values(packed_bytes, num_bits):
    unpacked_values = []
    current_byte = 0
    bits_written = 0
    mask = (1 << num_bits) - 1

    for byte in packed_bytes:
        current_byte <<= 8
        current_byte |= byte
        bits_written += 8

        while bits_written >= num_bits:
            bits_shift = bits_written - num_bits
            value = (current_byte >> bits_shift) & mask
            unpacked_values.append(value)
            bits_written -= num_bits

            if bits_shift > 0:
                current_byte &= (1 << bits_shift) - 1

    return unpacked_values

num_bits = count_bits(max(data))
all_bytes = pack_values(data, num_bits)
original = unpack_values(all_bytes, num_bits)

print(f"Using {num_bits} bits per value")

# Make sure the original data and the decompressed data are the same
for i in range(len(data)):
    if data[i] != original[i]:
        print(f'Error at {i}: {data[i]} != {original[i]}')

f = open(outputFile, 'wb')
f.write(bytes(all_bytes))
f.close()
    




