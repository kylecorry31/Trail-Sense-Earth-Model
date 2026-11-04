from .interfaces import ImageOperator
from ..size_budget import fit_to_budget


class FitToBudget(ImageOperator):
    """
    Chooses one of the encoded options (see WebpQualityOptions) of each image so that the total size is within the
    budget and the total error is as low as possible. The images are replaced by the encoded data of the chosen options
    (which Save writes as is).

    importance: how much the error of each image counts (by default, all of them count the same)
    error: the error of each option to minimize

    The metadata has the chosen option of each image, and the metadata of the options operator.
    """

    def __init__(self, options_operator, size_budget_bytes, importance=None, error="squared_error"):
        self.options_operator = options_operator
        self.size_budget_bytes = size_budget_bytes
        self.importance = importance
        self.error = error

    def apply(self, images):
        images, data = self.options_operator.apply(images)
        importance = self.importance or [1] * len(images)
        # Each option is paired with the importance of its image
        groups = [
            [(option, weight) for option in options]
            for options, weight in zip(data["options"], importance)
        ]
        chosen = fit_to_budget(
            groups,
            self.size_budget_bytes,
            size=lambda choice: len(choice[0]["data"]),
            cost=lambda choice: choice[1] * choice[0][self.error],
        )
        chosen = [option for option, _ in chosen]
        return [option["data"] for option in chosen], {**data, "chosen": chosen}
