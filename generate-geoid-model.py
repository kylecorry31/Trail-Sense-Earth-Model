from scripts import etopo, compression

etopo.download()
compression.minify(etopo.geoid_path, lambda x: int(x), -99999, 'output/geoids.webp', 100, False, (361, 181))