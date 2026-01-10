from scripts import progress
from .. import load_pixels

def process(images, *operators, show_progress=False):
    if images and isinstance(images[0], str):
        with progress.progress("Loading", total=len(images), disable=not show_progress) as pbar:
            new_images = []
            for path in images:
                new_images.append(load_pixels(path))
                pbar.update(1)
        images = new_images
    
    results = []
    with progress.progress("Processing", total=len(operators), disable=not show_progress) as pbar:
        for operator in operators:
            try:
                op_name = operator.__class__.__name__
                pbar.set_description(f"Processing [{op_name}]")
            except Exception:
                pass
            images, data = operator.apply(images)
            results.append(data)
            pbar.update(1)
    return images, results