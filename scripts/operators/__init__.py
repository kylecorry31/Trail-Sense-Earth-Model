def process(image, *operators):
    results = []
    for operator in operators:
        image, data = operator.apply(image)
        results.append(data)
    return image, results