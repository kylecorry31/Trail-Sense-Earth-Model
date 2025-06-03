import requests
import os
from .progress import progress
import zipfile


# https://www.ncei.noaa.gov/sites/g/files/anmtlf171/files/2025-01/WMM2025COF.zip
def download(redownload=False):
    with progress("Downloading WMM data", 1) as pbar:
        if not os.path.exists(f'source/wmm'):
            os.makedirs(f'source/wmm')
        if not os.path.exists(f'source/wmm/WMM.COF') or redownload:
            r = requests.get('https://www.ncei.noaa.gov/sites/g/files/anmtlf171/files/2025-01/WMM2025COF.zip')
            if r.status_code == 200:
                with open(f'source/wmm/WMM2025COF.zip', 'wb') as f:
                    f.write(r.content)
                with zipfile.ZipFile(f'source/wmm/WMM2025COF.zip', 'r') as zip_ref:
                    zip_ref.extractall(f'source/wmm')
                # Move all files from the WMM2025COF folder to the parent folder
                for file in os.listdir('source/wmm/WMM2025COF'):
                    os.rename(f'source/wmm/WMM2025COF/{file}', f'source/wmm/{file}')
                os.rmdir('source/wmm/WMM2025COF')
                os.remove(f'source/wmm/WMM2025COF.zip')
            else:
                raise Exception(f'Error {r.status_code} downloading {url}')
        pbar.update(1)

def process():
    with open('source/wmm/WMM.COF', 'r') as f:
        lines = f.readlines()
    
    g_coeffs = [[0]]
    h_coeffs = [[0]]
    delta_g = [[0]]
    delta_h = [[0]]

    for line in lines:
        cols = line.split()
        if len(cols) == 6:
            y = int(cols[0])
            g = float(cols[2])
            h = float(cols[3])
            d_g = float(cols[4])
            d_h = float(cols[5])

            if y >= len(g_coeffs):
                g_coeffs.append([])
                h_coeffs.append([])
                delta_g.append([])
                delta_h.append([])
            
            current_g_coeffs = g_coeffs[y]
            current_h_coeffs = h_coeffs[y]
            current_delta_g = delta_g[y]
            current_delta_h = delta_h[y]

            current_g_coeffs.append(g)
            current_h_coeffs.append(h)
            current_delta_g.append(d_g)
            current_delta_h.append(d_h)

    return {
        'g_coeff': g_coeffs,
        'h_coeff': h_coeffs,
        'delta_g': delta_g,
        'delta_h': delta_h
    }