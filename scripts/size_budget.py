import math


def fit_to_budget(groups, budget, size, cost):
    """
    Picks one option from each group so the total size is within the budget while the total cost is as low as
    possible. Each option is weighed as cost + penalty * size, where the penalty is the smallest one that fits.
    """

    def pick(group, penalty):
        return min(group, key=lambda option: cost(option) + penalty * size(option))

    def total_size(penalty):
        return sum(size(pick(group, penalty)) for group in groups)

    low, high = 1e-12, 1e3
    for _ in range(80):
        penalty = math.sqrt(low * high)
        if total_size(penalty) > budget:
            low = penalty
        else:
            high = penalty
    return [pick(group, high) for group in groups]
