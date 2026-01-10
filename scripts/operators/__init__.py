from .. import load_pixels

def process(images, *operators):
    if images and isinstance(images[0], str):
        images = [load_pixels(path) for path in images]
    
    results = []
    for operator in operators:
        images, data = operator.apply(images)
        results.append(data)
    return images, results