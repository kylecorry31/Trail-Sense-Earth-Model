import json
import argparse
import re
import os

parser = argparse.ArgumentParser()
parser.add_argument('filepath', help='Path to JSON file')
args = parser.parse_args()

with open(args.filepath + '/index.json', 'r') as f:
    data = json.load(f)

filename_to_number = {}

new_data = {}
new_data['c'] = data['compression_method']
new_data['v'] = data['version']
new_data['r'] = data['resolution_arc_seconds']
new_data['wm'] = data.get('has_water_mask', False)
new_data['w'] = 0
new_data['h'] = 0 
new_data['f'] = []

width_height_counts = {}

i = 0
for file in data['files']:
    filename_to_number[file['filename']] = i
    new_file = [
        i,
        file['a'] if int(file['a']) != file['a'] else int(file['a']),
        file['b'] if int(file['b']) != file['b'] else int(file['b']),
        int(file['latitude_start']),
        int(file['longitude_start']),
        int(file['latitude_end']),
        int(file['longitude_end']),
        int(file['width']),
        int(file['height'])
    ]
    w_h = (file['width'], file['height'])
    if w_h not in width_height_counts:
        width_height_counts[w_h] = 0
    width_height_counts[w_h] += 1
    new_data['f'].append(new_file)
    i += 1

most_common_w_h = max(width_height_counts, key=width_height_counts.get)

new_data['w'] = most_common_w_h[0]
new_data['h'] = most_common_w_h[1]

for file in new_data['f']:
    if file[7] == new_data['w'] and file[8] == new_data['h']:
        file.pop()
        file.pop()

if os.path.exists('dem-shrunk'):
    for root, dirs, files in os.walk('dem-shrunk', topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir('dem-shrunk')

os.makedirs('dem-shrunk', exist_ok=True)

images = os.listdir(args.filepath)
for image in images:
    if image.endswith('.webp'):
        old_index = filename_to_number[image]
        new_index = None
        for file in new_data['f']:
            if file[0] == old_index:
                new_index = file[0]
                break
        if new_index is not None:
            with open(os.path.join(args.filepath, image), 'rb') as f_in:
                data = f_in.read()
            with open(os.path.join('dem-shrunk', f'{new_index}.webp'), 'wb') as f_out:
                f_out.write(data)

with open('dem-shrunk/index.json', 'w') as f:
    index = json.dumps(new_data)
    index = re.sub(r"\s", "", index)
    f.write(index)