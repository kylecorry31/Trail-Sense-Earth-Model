def process(images, *operators):
    results = []
    for operator in operators:
        images, data = operator.apply(images)
        results.append(data)
    return images, results