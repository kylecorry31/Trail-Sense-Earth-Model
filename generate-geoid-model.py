from scripts import etopo
from scripts.operators import process
from scripts.operators import LinearCompression, Resize, Save

etopo.download()
_, results = process(
    [etopo.geoid_path],
    LinearCompression(),
    Resize((360, 180)),
    Save(["output/geoids.webp"], quality=100, lossless=False),
    show_progress=True,
)

# Print the coefficients
print(results.of(LinearCompression))
