from scripts import tidal_corrections

# INPUT
year = 2025

######## Program, don't modify ########
corrections = tidal_corrections.get_corrections(year)

# Print as a Kotlin map
print('private val corrections = mutableMapOf(')

for constituent, correction in corrections.items():
    if constituent[0].isdigit():
        constituent = "_" + constituent
    print(f'    TideConstituent.{constituent} to Pair({
          correction['f']}, {correction['uv']}),')

print(')')
