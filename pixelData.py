import struct
from sys import path
import os.path


class CompressionError(Exception):

    """bmp file have compression"""

    pass


class PixelData(object):

    """pulls out the pixel data from the BMP file"""

    def __init__(self, path_image):
        super(PixelData, self).__init__()
        self._pathImage = path_image
        with open(self._pathImage, "rb") as image:
            self._data = image.read()

            self._offsetPixelData = struct.unpack("i", self._data[10:14])[0]

            self._width_image = struct.unpack("i", self._data[18:22])[0]
            self._height_image = struct.unpack("i", self._data[22:26])[0]

            pixel_size_bit = struct.unpack("h", self._data[28:30])[0]
            if pixel_size_bit <= 8:
                self._pixel_size = 1
            else:
                self._pixel_size = pixel_size_bit // 8

            compression = struct.unpack("i", self._data[30:34])[0]
            size_header_bitmap_info = struct.unpack("i", self._data[14:18])[0]
            if size_header_bitmap_info > 12 and compression:
                raise CompressionError("Bmp file have compression")

    def get_pixel_data(self):
        """returns the pixel data of the image"""
        image_size =\
            self._height_image * self._width_image * self._pixel_size
        self._pixel_array = self._data[
            self._offsetPixelData:self._offsetPixelData + image_size]
        return(self._pixel_array)

    def write_new_image(self, pixel_data, path_new_image=None):
        """writes a new image"""
        data = None
        with open(self._pathImage, "rb") as image:
            data = image.read()

        if path_new_image:
            path_out_image = path_new_image
        else:
            path_out_image = os.path.join(path[0], "steganography.bmp")
        with open(path_out_image, "wb") as image:
            image.write(data[:self._offsetPixelData])
            image.write(pixel_data)
            image.write(data[self._offsetPixelData + len(pixel_data):])

    def get_pixel_size(self):
        """returns the size of the pixels"""
        return(self._pixel_size)

    def get_width(self):
        """returns the width"""
        return(self._width_image)

    def get_height(self):
        """returns the height"""
        return(self._height_image)
