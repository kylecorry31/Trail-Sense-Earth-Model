from .interfaces import ImageOperator
import heapq
import numpy as np


class Quadtree(ImageOperator):
    """
    Divides the images into a quadtree of cells, where the cells are large where the images change slowly and
    small where they change quickly, and outputs a label image with the number (starting at 1) of the cell that
    each min_size pixel is in (0 where there is no cell). The cells are shared by all of the images and exist wherever
    the first image has data.

    Starting from every base_size block (in pixels) which has data, the block with the largest change between its
    4 children and itself (the relative euclidean distance across all of the images) is split first, until the
    cell budget is used or the cells are min_size. The base size must be min_size * 2^n.
    """

    def __init__(
        self,
        base_size,
        min_size,
        cell_budget,
        invalid_value=-999,
        reference_floor=1e-6,
    ):
        self.base_size = base_size
        self.min_size = min_size
        self.cell_budget = cell_budget
        self.invalid_value = invalid_value
        self.reference_floor = reference_floor

    def __sizes(self):
        sizes = [self.base_size]
        while sizes[-1] > self.min_size:
            sizes.append(sizes[-1] // 2)
        assert sizes[-1] == self.min_size, "The base size must be the min size times a power of 2"
        return sizes

    @staticmethod
    def __block_sum(values, size, dtype):
        channels, height, width = values.shape
        return values.reshape(channels, height // size, size, width // size, size).sum(
            axis=(2, 4), dtype=dtype
        )

    def apply(self, images):
        sizes = self.__sizes()
        stack = np.stack(images)
        valid = stack != self.invalid_value
        values = np.where(valid, stack, 0)
        del stack

        means = {}
        counts = {}
        for size in sizes:
            counts[size] = self.__block_sum(valid, size, np.int32)
            sums = self.__block_sum(values, size, np.float64)
            means[size] = sums / np.maximum(counts[size], 1)
        del values

        exists = {size: counts[size][0] > 0 for size in sizes}

        # The relative change from each block to its parent, for the blocks which are not the base size
        change = {}
        for size in sizes[1:]:
            parent = np.repeat(np.repeat(means[size * 2], 2, axis=1), 2, axis=2)
            parent_valid = np.repeat(np.repeat(counts[size * 2] > 0, 2, axis=1), 2, axis=2)
            both = (counts[size] > 0) & parent_valid
            distance = np.sqrt((np.abs(means[size] - parent) ** 2 * both).sum(axis=0))
            reference = np.sqrt((np.abs(parent) ** 2 * parent_valid).sum(axis=0))
            change[size] = distance / np.maximum(reference, self.reference_floor)

        def children(size, row, column):
            child_size = size // 2
            return [
                (2 * row + dr, 2 * column + dc)
                for dr in (0, 1)
                for dc in (0, 1)
                if exists[child_size][2 * row + dr, 2 * column + dc]
            ]

        def candidate(size, row, column):
            kids = children(size, row, column)
            cost = len(kids) - 1
            gain = max(change[size // 2][r, c] for r, c in kids)
            # Splitting a block which only has one child with data is free
            priority = gain + (1e6 if cost == 0 else 0)
            return -priority, size, row, column, cost

        queue = [
            candidate(self.base_size, int(row), int(column))
            for row, column in np.argwhere(exists[self.base_size])
            if self.base_size > self.min_size
        ]
        heapq.heapify(queue)
        cell_count = int(exists[self.base_size].sum())

        split = set()
        while queue and cell_count < self.cell_budget:
            _, size, row, column, cost = heapq.heappop(queue)
            if cell_count + cost > self.cell_budget:
                continue
            split.add((size, row, column))
            cell_count += cost
            if size // 2 > self.min_size:
                for r, c in children(size, row, column):
                    heapq.heappush(queue, candidate(size // 2, r, c))

        height, width = images[0].shape
        labels = np.zeros((height // self.min_size, width // self.min_size), dtype=np.int32)
        label = 0
        pending = [
            (self.base_size, int(row), int(column))
            for row, column in np.argwhere(exists[self.base_size])
        ]
        while pending:
            size, row, column = pending.pop()
            if (size, row, column) in split:
                pending.extend((size // 2, r, c) for r, c in children(size, row, column))
            else:
                label += 1
                pixels = size // self.min_size
                labels[row * pixels : (row + 1) * pixels, column * pixels : (column + 1) * pixels] = label

        return [labels], {}
