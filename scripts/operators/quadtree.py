from .interfaces import ImageOperator
import heapq
import numpy as np


class Quadtree(ImageOperator):
    """
    Condenses the images into a quadtree of cells, where the cells are large where the images change slowly and
    small where they change quickly. The images are condensed together (one value per cell per image) so they
    share the same cells, which exist wherever the first image has data.

    Starting from every base_size block (in pixels) which has data, the block with the largest change between its
    4 children and itself (the relative euclidean distance across all of the images) is split first, until the
    cell budget is used or the cells are min_size. The base size must be min_size * 2^n.

    The metadata includes indices_x and indices_y images (at min_size pixel resolution) which map each pixel to the
    position of its cell in the condensed images. The condensed images are final_width wide, with the cells ordered
    along a Hilbert curve so neighboring cells are next to each other, which makes the images compress better.
    """

    def __init__(
        self,
        base_size,
        min_size,
        cell_budget,
        final_width,
        invalid_value=-999,
        reference_floor=1e-6,
    ):
        self.base_size = base_size
        self.min_size = min_size
        self.cell_budget = cell_budget
        self.final_width = final_width
        self.invalid_value = invalid_value
        self.reference_floor = reference_floor

    def __sizes(self):
        sizes = [self.base_size]
        while sizes[-1] > self.min_size:
            sizes.append(sizes[-1] // 2)
        assert sizes[-1] == self.min_size, "The base size must be the min size times a power of 2"
        return sizes

    @staticmethod
    def __hilbert_distance(x, y, order):
        distance = 0
        step = 1 << (order - 1)
        while step > 0:
            rx = 1 if x & step else 0
            ry = 1 if y & step else 0
            distance += step * step * ((3 * rx) ^ ry)
            if ry == 0:
                if rx == 1:
                    x, y = step - 1 - x, step - 1 - y
                x, y = y, x
            step //= 2
        return distance

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

        cells = []
        pending = [
            (self.base_size, int(row), int(column))
            for row, column in np.argwhere(exists[self.base_size])
        ]
        while pending:
            size, row, column = pending.pop()
            if (size, row, column) in split:
                pending.extend((size // 2, r, c) for r, c in children(size, row, column))
            else:
                cells.append((row * size, column * size, size))
        height, width = images[0].shape
        order = max(1, int(np.ceil(np.log2(max(height, width) // self.min_size))))
        cells.sort(
            key=lambda cell: self.__hilbert_distance(
                (cell[1] + cell[2] // 2) // self.min_size,
                (cell[0] + cell[2] // 2) // self.min_size,
                order,
            )
        )

        rows = -(-len(cells) // self.final_width)
        assert rows < 255, f"Too many cells to index: {len(cells)}"

        output = np.full((len(images), rows * self.final_width), self.invalid_value, dtype=np.float64)
        cell_array = np.array(cells)
        for size in sizes:
            in_size = np.flatnonzero(cell_array[:, 2] == size)
            if len(in_size) == 0:
                continue
            block_rows = cell_array[in_size, 0] // size
            block_columns = cell_array[in_size, 1] // size
            cell_means = means[size][:, block_rows, block_columns]
            cell_has_data = counts[size][:, block_rows, block_columns] > 0
            output[:, in_size] = np.where(cell_has_data, cell_means, self.invalid_value)

        indices_x = np.zeros((height // self.min_size, width // self.min_size))
        indices_y = np.zeros_like(indices_x)
        for i, (row, column, size) in enumerate(cells):
            r = slice(row // self.min_size, (row + size) // self.min_size)
            c = slice(column // self.min_size, (column + size) // self.min_size)
            indices_x[r, c] = i % self.final_width + 1
            indices_y[r, c] = i // self.final_width + 1

        condensed = [image.reshape(rows, self.final_width) for image in output]
        return condensed, {"indices_x": indices_x, "indices_y": indices_y, "cells": cells}
