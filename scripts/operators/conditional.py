from .interfaces import ImageOperator


class Conditional(ImageOperator):
    def __init__(self, condition, operator_if_true, operator_if_false=None):
        self.condition = condition
        self.operator_if_true = operator_if_true
        self.operator_if_false = operator_if_false

    def apply(self, images):
        output = []
        metadata = []
        for image in images:
            evaluated_condition = (
                self.condition
                if not callable(self.condition)
                else self.condition(image)
            )

            operation = (
                self.operator_if_true if evaluated_condition else self.operator_if_false
            )
            if operation is None:
                output.append(image)
                continue
            result, meta = operation.apply([image])
            metadata.append(meta)
            for i in result:
                output.append(i)
        return output, {"metadata": metadata}
