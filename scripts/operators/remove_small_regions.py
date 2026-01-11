from .interfaces import ImageOperator
import numpy as np
from skimage import measure


class RemoveSmallRegions(ImageOperator):
    def __init__(
        self, color, max_size=10, invalid_colors=None, default_fill=None, search_space=2
    ):
        self.color = color
        self.max_size = max_size
        self.invalid_colors = invalid_colors or []
        self.default_fill = default_fill
        self.search_space = search_space

    def __remove_small_regions(
        self,
        image,
        color,
        max_size=10,
        invalid_colors=None,
        default_fill=None,
        search_space=2,
    ):
        distances = np.linalg.norm(
            image.astype(np.int16) - np.array(color).astype(np.int16), axis=-1
        )
        mask = distances <= 4

        # Label connected components
        labeled = measure.label(mask)
        props = sorted(measure.regionprops(labeled), key=lambda r: r.area, reverse=True)

        cleaned = image.copy()

        for region in props:
            if region.area <= max_size:
                # Get coordinates of the small region
                coords = region.coords

                # Find the most common neighboring color for the entire region
                all_neighbors = []
                for coord in coords:
                    y, x = coord
                    # Search eighborhood for non-region pixels
                    neighbors = image[
                        max(0, y - (search_space - 1)) : y + search_space,
                        max(0, x - (search_space - 1)) : x + search_space,
                    ]
                    neighbors_mask = (
                        labeled[
                            max(0, y - (search_space - 1)) : y + search_space,
                            max(0, x - (search_space - 1)) : x + search_space,
                        ]
                        != region.label
                    )
                    valid_neighbors = neighbors[neighbors_mask]

                    if len(valid_neighbors) > 0:
                        if invalid_colors is None:
                            all_neighbors.extend(valid_neighbors)
                        else:
                            invalid_colors_array = np.array(invalid_colors)
                            valid_mask = ~np.any(
                                np.all(
                                    valid_neighbors[:, None]
                                    == invalid_colors_array[None, :],
                                    axis=-1,
                                ),
                                axis=1,
                            )
                            all_neighbors.extend(valid_neighbors[valid_mask])

                if len(all_neighbors) > 0:
                    # Find the most frequent neighbor color across all boundary pixels
                    all_neighbors = np.array(all_neighbors)
                    unique_colors, counts = np.unique(
                        all_neighbors.reshape(-1, 3), axis=0, return_counts=True
                    )
                    most_frequent_idx = np.argmax(counts)
                    replacement_color = unique_colors[most_frequent_idx]
                else:
                    replacement_color = (
                        default_fill if default_fill is not None else color
                    )

                # Fill the entire region with the same color
                for coord in coords:
                    y, x = coord
                    cleaned[y, x] = replacement_color

        return cleaned

    def apply(self, images):
        output = []
        for image in images:
            result = self.__remove_small_regions(
                image,
                self.color,
                self.max_size,
                invalid_colors=self.invalid_colors,
                default_fill=self.default_fill,
                search_space=self.search_space,
            )
            output.append(result)
        return output, {}
