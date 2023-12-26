from scripts import etopo, compression, natural_earth

def constrain(value, min, max):
    if value < min:
        return min
    if value > max:
        return max
    return value

etopo.download()
natural_earth.download()
etopo.process_dem()
resolution = (2880, 1440)
compression.minify(etopo.dem_land_path, lambda x: constrain(x, -10000, 0), -99999, 'output/dem-1.webp', 100, False, resolution)
compression.minify(etopo.dem_land_path, lambda x: constrain(x, 0, 800), -99999, 'output/dem-2.webp', 100, False, resolution)
compression.minify(etopo.dem_land_path, lambda x: constrain(x, 800, 10000), -99999, 'output/dem-3.webp', 100, False, resolution)