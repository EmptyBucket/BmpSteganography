from sys import path
from pixelData import PixelData
from os.path import getsize
import os.path


class NotBMPError(Exception):

    """file is not type BMP"""

    pass


class LengthError(Exception):

    """length error information"""

    pass


class Steganography(object):

    """hide text information from the console or input file in BMP "
    "format image. Or removal of text from the image in BMP format "
    "console or output text file"""

    def __init__(self, image_path):
        super(Steganography, self).__init__()
        self._image_path = image_path
        if self._image_path[-4:] != ".bmp":
            raise NotBMPError("File is not type BMP")
        self._pixel_data = PixelData(self._image_path)

    def _bin_message(self, information, len_byte_message):
        bin_information_len = bin(len_byte_message)[2:].zfill(32)

        bin_information = []
        bin_information.append(bin_information_len)

        for byte in information:
            bin_byte = bin(byte)[2:].zfill(8)
            bin_information.append(bin_byte)
        else:
            bin_information = ''.join(bin_information)

        list_bit = tuple(map(int, bin_information))

        return list_bit

    def _separation(self, bin_message, pixel_data):
        """divides the binary data is too big"""
        separation_bin_message = []

        size_image = pixel_data.get_width() *\
            pixel_data.get_height() * pixel_data.get_pixel_size()

        valueblock = len(bin_message) // size_image
        ost = len(bin_message) % size_image

        for i in range(valueblock):
            block = bin_message[size_image * i:size_image * (i + 1)]
            separation_bin_message.append(block)
        else:
            try:
                block = bin_message[
                    size_image * (i + 1):size_image * (i + 1) + ost]
            except UnboundLocalError:
                block = bin_message[:ost]
            if block:
                separation_bin_message.append(block)

        return separation_bin_message

    @staticmethod
    def _set_bit(byte, index, bit):
        """sets bit number"""
        mask = 1 << index
        byte &= ~mask
        if bit:
            byte |= mask
        return byte

    def hide_information(
            self, information, out_file=None):
        """hide information in the image data"""
        if type(information) is str:
            information = information.encode()
        len_byte_message = len(information)

        capacity_image = self._pixel_data.get_height() *\
            self._pixel_data.get_width() * self._pixel_data.get_pixel_size()
        if capacity_image < len_byte_message + 4:
            raise LengthError('Information does not fit into the picture. \
                Length of the information: {0}. Сapacity image: \
                {1}'.format(len_byte_message, capacity_image))

        bin_message = self._bin_message(information, len_byte_message)

        separation_bin_message =\
            self._separation(bin_message, self._pixel_data)

        byte_array = self._pixel_data.get_pixel_data()
        number_bit = 0
        byte_array = list(byte_array)
        for piece_bin_message in separation_bin_message:
            setBit = (i for i in piece_bin_message)
            for i in range(len(byte_array)):
                try:
                    nextBit = next(setBit)
                    byte_array[i] = Steganography._set_bit(
                            byte_array[i], number_bit, nextBit)
                except StopIteration:
                    break
            number_bit += 1
        self._pixel_data.write_new_image(bytes(byte_array), out_file)

    @staticmethod
    def _get_bit(byte, index):
        """returns the number of bits"""
        bit = str(int(byte & 1 << index != 0))
        return bit

    @staticmethod
    def _get_allByte(bin_information):
        """returns all bytes of binary information"""
        counter = 0
        byte = ""
        all_bytes = []
        for bit in bin_information:
            byte += bit
            counter += 1

            if counter == 8:
                all_bytes.append(int(byte, 2))
                byte = ""
                counter = 0

        return bytes(all_bytes)

    def unhide_information(self, out_file=None):
        """discloses information from image"""
        byteArray = self._pixel_data.get_pixel_data()

        len_bit_information = ""
        len_information = None

        number_bit = 0
        get_byte = (i for i in byteArray)
        for i in range(32):
            try:
                nextByte = next(get_byte)
                len_bit_information +=\
                    Steganography._get_bit(nextByte, number_bit)
            except StopIteration:
                number_bit += 1
                get_byte = (i for i in byteArray)
                nextByte = next(get_byte)
                len_bit_information +=\
                    Steganography._get_bit(nextByte, number_bit)
        else:
            len_information = int(len_bit_information, 2) * 8

        information_need_bits = ""
        for i in range(len_information):
            try:
                nextByte = next(get_byte)
                information_need_bits +=\
                    Steganography._get_bit(nextByte, number_bit)
            except StopIteration:
                number_bit += 1
                get_byte = (i for i in byteArray)
                nextByte = next(get_byte)
                information_need_bits +=\
                    Steganography._get_bit(nextByte, number_bit)

        comlete_information = Steganography._get_allByte(information_need_bits)

        if out_file:
            with open(out_file, "wb") as out_file:
                out_file.write(comlete_information)
        else:
            print(comlete_information.decode('utf-8'))

    @staticmethod
    def test():
        """testing method"""
        stegH = Steganography(os.path.join(path[0], "test", "in_image.bmp"))
        lever = False

        print("Test hide/unhide english txt:")
        with open(os.path.join(
                path[0], "test", "input1.txt"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output1.txt"))
            if getsize(os.path.join(path[0], "test", "input1.txt")) == getsize(
                    os.path.join(path[0], "test", "output1.txt")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Test hide/unhide russian txt:")
        with open(os.path.join(
                path[0], "test", "input5.txt"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output5.txt"))
            if getsize(os.path.join(path[0], "test", "input5.txt")) == getsize(
                    os.path.join(path[0], "test", "output5.txt")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Test hide/unhide en/ru txt:")
        with open(os.path.join(
                path[0], "test", "input6.txt"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output6.txt"))
            if getsize(os.path.join(path[0], "test", "input6.txt")) == getsize(
                    os.path.join(path[0], "test", "output6.txt")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Test hide/unhide png:")
        with open(os.path.join(
                path[0], "test", "input2.png"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output2.png"))
            if getsize(os.path.join(path[0], "test", "input2.png")) == getsize(
                    os.path.join(path[0], "test", "output2.png")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Test hide/unhide rar:")
        with open(os.path.join(
                path[0], "test", "input3.rar"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output3.rar"))
            if getsize(os.path.join(path[0], "test", "input3.rar")) == getsize(
                    os.path.join(path[0], "test", "output3.rar")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Test hide/unhide exe:")
        with open(os.path.join(
                path[0], "test", "input4.exe"), 'rb') as inputFile:
            stegH.hide_information(
                inputFile.read(), os.path.join(path[0], "test", "steg.bmp"))

            stegU = Steganography(os.path.join(path[0], "test", "steg.bmp"))
            stegU.unhide_information(
                os.path.join(path[0], "test", "output4.exe"))
            if getsize(os.path.join(
                path[0], "test", "input4.exe")) == getsize(
                    os.path.join(path[0], "test", "output4.exe")):
                print("Verification was successful")
            else:
                print("Validation fails")
                lever = True

        print("Complete test")

        return lever
