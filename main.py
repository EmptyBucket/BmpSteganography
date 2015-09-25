import argparse
from steganography import Steganography
import sys


def normal():
        container = args.image
        mode = args.mode
        try:
            steg = Steganography(container)
            if mode == "hide":
                if args.in_file:
                    information = open(args.in_file, 'rb').read()
                else:
                    information = input("Enter concealed text:\n")
                steg.hide_information(information, args.out_file)
            elif mode == "unhide":
                steg.unhide_information(args.out_file)
        except Exception as e:
            sys.exit("Error: {0}".format(e))


def test():
    lever = Steganography.test()
    if not lever:
        print("Test is passed")
    else:
        print("Test fails")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Steganography",
        description="purpose tools - hides the text information "
        "from the console, or any given file in the image. Reveals "
        "hidden in the image information in the console or in the output"
        " file.",
        epilog="Copyright (C) 2015 Politov Alexey Version 1.0")
    sub_parsers = parser.add_subparsers(title="use normal or test mode")

    normal_parser = sub_parsers.add_parser("normal")
    normal_parser.add_argument(
        "mode", choices=["hide", "unhide"],
        help="Mode (Hide/Unhide)", default="hide")
    normal_parser.add_argument("image", type=str, help="Container")
    normal_parser.add_argument(
        "-i", "--in_file", action="store",
        type=str, help="Hide file")
    normal_parser.add_argument(
        "-o", "--out_file", action="store",
        type=str, help="Output file - image with hidden "
        "information (use modes hide) or - file whose "
        "information has been hidden (use modes unhide)")
    normal_parser.set_defaults(func=normal)

    testParser = sub_parsers.add_parser("test")
    testParser.set_defaults(func=test)

    args = parser.parse_args()
    try:
        args.func()
    except AttributeError:
        parser.parse_args(["-h"])
