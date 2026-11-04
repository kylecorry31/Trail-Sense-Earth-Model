from .interfaces import ImageOperator


class CompoundOperator(ImageOperator):
    """
    An operator composed of other operators. Subclasses implement operators(). When used in process, the steps are run
    (and their results recorded) as if they were listed directly, so results.of(Step) finds them.
    """

    def operators(self):
        raise NotImplementedError

    def apply(self, images):
        metadata = []
        for operator in self.operators():
            images, data = operator.apply(images)
            metadata.append(data)
        return images, {"metadata": metadata}
