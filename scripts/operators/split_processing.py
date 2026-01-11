from .interfaces import ImageOperator


class SplitProcessing(ImageOperator):
    def __init__(self, *operators):
        self.operators = operators

    def apply(self, images):
        output = []
        data = {"data": []}
        for image in images:
            image_data = []
            for operator in self.operators:
                image, operator_data = operator.apply([image])
                image_data.append(operator_data)
            for i in image:
                output.append(i)
            data["data"].append(image_data)
        return output, data
