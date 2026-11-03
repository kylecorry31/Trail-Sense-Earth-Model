import subprocess


def encode_gray(image, quality):
    """
    Encodes an 8-bit image as lossy WebP with cwebp (the webp package), since PIL can't turn off the adaptive
    quantization which makes smooth data blocky at lower qualities.
    """
    height, width = image.shape
    pgm = f"P5\n{width} {height}\n255\n".encode() + image.tobytes()
    result = subprocess.run(
        ["cwebp", "-quiet", "-q", str(quality), "-m", "6", "-sns", "0", "-segments", "1", "-o", "-", "--", "-"],
        input=pgm,
        capture_output=True,
        check=True,
    )
    return result.stdout
