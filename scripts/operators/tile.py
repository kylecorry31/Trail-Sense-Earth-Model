from .interfaces import ImageOperator
import numpy as np


class Tile(ImageOperator):
    def __init__(self, tile_size, max_dimensions=False):
        self.tile_size = tile_size
        self.max_dimensions = max_dimensions

    def __get_tile_size(self, image_shape):
        max_height, max_width = self.tile_size
        width = image_shape[1]
        height = image_shape[0]
        dividers = [5, 4, 3, 2, 1]
        tile_width = width
        tile_height = height
        for divider in dividers:
            if width % divider == 0 and width // divider < max_width:
                tile_width = width // divider
            if height % divider == 0 and height // divider < max_height:
                tile_height = height // divider
        return tile_height, tile_width

    def apply(self, images):
        output = []
        tile_metadata = []
        for image in images:
            tile_height, tile_width = (
                self.__get_tile_size(image.shape)
                if self.max_dimensions
                else self.tile_size
            )
            tiles_x = int(np.ceil(image.shape[1] / tile_width))
            tiles_y = int(np.ceil(image.shape[0] / tile_height))
            tile_metadata.append(
                {
                    "tile_width": tile_width,
                    "tile_height": tile_height,
                    "rows": tiles_y,
                    "columns": tiles_x,
                }
            )
            for ty in range(tiles_y):
                for tx in range(tiles_x):
                    x_start = tx * tile_width
                    y_start = ty * tile_height
                    x_end = min(x_start + tile_width, image.shape[1])
                    y_end = min(y_start + tile_height, image.shape[0])
                    tile = image[y_start:y_end, x_start:x_end]
                    output.append(tile)
        return output, {"tiles": tile_metadata}
