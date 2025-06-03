from scripts import etopo, compression, load_pixels

etopo.download()
compression.minify(etopo.geoid_path, lambda x: x, -99999, 'output/geoids.webp', 100, False, (361, 181))

harmonics = compression.spherical_harmonics(etopo.geoid_path, lambda x: x, -99999, 3_000_000, 'output/geoids_reconstructed.webp', True)

code = "private val gCoeff = arrayOf(\n"
for row in harmonics['g']:
    code += "    byteArrayOf("
    code += ", ".join(f"{int(val)}" for val in row)
    code += "),\n"

code += ");\n\n"

code += "private val hCoeff = arrayOf(\n"
for row in harmonics['h']:
    code += "    byteArrayOf("
    code += ", ".join(f"{int(val)}" for val in row)
    code += "),\n"

code += ");\n\n"

print(code)