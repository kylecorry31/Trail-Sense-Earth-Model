from PIL import Image
from scripts import etopo
from scripts.report import print_stretch
from scripts.operators import process, Stretch, LinearCompression, Resize, Save

etopo.download()
_, results = process(
    [etopo.geoid_path],
    Resize((540, 270), resample=Image.BOX, exact=True),
    Stretch(),
    Save(["output/geoids.webp"], quality=95, lossless=False, adaptive_quantization=False),
    show_progress=True,
)

print_stretch("geoid", results.of(LinearCompression)["coefficients"])
