from . import load_pixels, to_tif

def clip_uninhabitable_areas(image, north=72, south=-60):
    height = image.shape[0]

    north_pixel = max(0, min(height, int((90 - north) / 180 * height)))
    south_pixel = max(0, min(height, int((90 - south) / 180 * height)))

    return image[north_pixel:south_pixel, :]

def clip_uninhabitable_areas_tif(image_path, output_path, north=72, south=-60):
    image = load_pixels(image_path)
    image = clip_uninhabitable_areas(image, north, south)
    to_tif(image, output_path)