import imageio
import glob
import re
import argparse
import os


def natural_sort_key(s):
    """
    Generate a key for natural sorting. It splits the input string into a list
    of strings and integers, which is suitable for correct numeric sorting.
    """
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


def load_images(directory, input, output, duration):
    regex = os.path.join(directory, input)
    filenames = sorted(glob.glob(regex), key=natural_sort_key)
    output_gif = f"{output}.gif" if not output.endswith(".gif") else output
    images = [imageio.v3.imread(filename) for filename in filenames]
    imageio.v3.imwrite(output_gif, images, duration=duration, loop=0)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-regexp", type=str, required=True, help="The input file regexp"
    )
    parser.add_argument("--output", type=str, required=True, help="The output file")
    parser.add_argument(
        "--directory", type=str, required=True, help="The output directory"
    )
    parser.add_argument(
        "--duration", type=float, default=0.1, help="The duration of each frame"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    load_images(args.directory, args.input_regexp, args.output, args.duration)


if __name__ == "__main__":
    main()
