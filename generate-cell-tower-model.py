from scripts import opencellid, compression

opencellid.download()
towers = opencellid.process(0.03)

compression.minify('images/opencellid/cell_towers.tif', lambda x: x, -99999, 'output/cell_towers.webp', 100, True, a_override=1, b_override=0)