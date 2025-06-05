from .interfaces import ImageOperator
import numpy as np

class Index(ImageOperator):
    def __init__(self, condenser=None, final_width=255, invalid_value=-999):
        self.condenser = condenser
        self.final_width = final_width
        self.invalid_value = invalid_value

    def __create_condensed_image(self, image, valid_indices, final_width):
        original_dtype = image.dtype
        updated = image[valid_indices]
        total_values = len(updated)
        updated = np.append(updated, np.zeros(final_width - (total_values % final_width)))
        updated = updated.reshape((-1, final_width))
        return updated.astype(original_dtype)

    def apply(self, image):
        if self.condenser is not None:
            return self.condenser(image), {}
        non_zero_bool_array = image != self.invalid_value
        indices_x = np.zeros(image.shape)
        indices_y = np.zeros(image.shape)
        non_zero_indices = np.argwhere(non_zero_bool_array)
        for i in range(len(non_zero_indices)):
            source_x = non_zero_indices[i][1]
            source_y = non_zero_indices[i][0]
            destination_x = i % self.final_width + 1
            destination_y = i // self.final_width + 1
            indices_x[source_y, source_x] = destination_x
            indices_y[source_y, source_x] = destination_y
        data = {
            'indices_x': indices_x,
            'indices_y': indices_y,
            'condenser': lambda i: self.__create_condensed_image(i, non_zero_bool_array, self.final_width),
            'non_zero_bool_array': non_zero_bool_array
        }
        return data['condenser'](image), data