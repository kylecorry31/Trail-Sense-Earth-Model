from .interfaces import ImageOperator
from .. import save_compressed, create_image
import numpy as np
from PIL import Image

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

    def apply(self, images):
        if self.condenser is not None:
            return [self.condenser(image) for image in images], {}
        data = None
        output = []
        for image in images:
            if data is not None:
                output.append(data['condenser'](image))
            else:
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
                output.append(data['condenser'](image))
        return output, data

class LinearCompression(ImageOperator):
    def __init__(self, a=None, b=None, calculate_per_image=False):
        self.a = a
        self.b = b
        self.calculate_per_image = calculate_per_image

    def apply(self, images):
        # Calculate global min/max if needed
        data_a = self.a
        data_b = self.b

        if not self.calculate_per_image and (data_a is None or data_b is None):
             min_value = np.inf
             max_value = -np.inf
             for image in images:
                 min_value = min(min_value, np.min(image))
                 max_value = max(max_value, np.max(image))
             
             if np.isinf(min_value):
                 data_b = 0
                 data_a = 1
             else:
                 data_b = -min_value
                 # Avoid division by zero
                 denom = max_value + data_b
                 data_a = 255 / denom if denom != 0 else 1
        else:
            # Use provided or default (will be overwritten if calculate_per_image is True)
            data_a = self.a if self.a is not None else 1.0
            data_b = self.b if self.b is not None else 0.0

        output = []
        for image in images:
            current_a = data_a
            current_b = data_b
            
            if self.calculate_per_image:
                 local_min = np.min(image)
                 local_max = np.max(image)
                 current_b = -local_min
                 denom = local_max + current_b
                 current_a = 255 / denom if denom != 0 else 1

            # Apply compression
            compressed = (image + current_b) * current_a
            
            # Cast to uint8
            output.append(compressed.astype(np.uint8))
        
        # Return the global a/b if we calculated them globally
        metadata = {}
        if not self.calculate_per_image:
            metadata['a'] = data_a
            metadata['b'] = data_b

        return output, metadata

class Split16Bits(ImageOperator):
    def apply(self, images):
        output = []
        for image in images:
            lower_bits = (image & 0xFF).astype(np.uint8)
            upper_bits = ((image >> 8) & 0xFF).astype(np.uint8)
            output.append(lower_bits)
            output.append(upper_bits)
        return output, {}