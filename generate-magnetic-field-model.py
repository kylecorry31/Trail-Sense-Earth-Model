from scripts import wmm

wmm.download()
data = wmm.process()

# Format as Java
java = "static private final float[][] G_COEFF = new float[][]{\n"

for row in data['g_coeff']:
    java += "    {"
    java += ", ".join(f"{val:.1f}f" for val in row)
    java += "},\n"

java = java[:-2]
java += "};\n"

java += "static private final float[][] H_COEFF = new float[][]{\n"
for row in data['h_coeff']:
    java += "    {"
    java += ", ".join(f"{val:.1f}f" for val in row)
    java += "},\n"
java = java[:-2]
java += "};\n"

java += "static private final float[][] DELTA_G = new float[][]{\n"
for row in data['delta_g']:
    java += "    {"
    java += ", ".join(f"{val:.1f}f" for val in row)
    java += "},\n"
java = java[:-2]
java += "};\n"

java += "static private final float[][] DELTA_H = new float[][]{\n"
for row in data['delta_h']:
    java += "    {"
    java += ", ".join(f"{val:.1f}f" for val in row)
    java += "},\n"
java = java[:-2]
java += "};"

print(java)