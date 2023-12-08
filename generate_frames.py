import argparse
import glob
import os
import re
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import tqdm
from PIL import Image, ImageDraw, ImageFont


def natural_sort_key(s):
    """
    Generate a key for natural sorting. It splits the input string into a list
    of strings and integers, which is suitable for correct numeric sorting.
    """
    return [
        int(text) if text.isdigit() else text.lower() for text in re.split(r"(\d+)", s)
    ]


def float_to_binary(ftype="float"):
    if ftype == "float":
        sign = "0"
        exponent = "0" * 8
        mantissa = "0" * 23
    elif ftype == "double":
        sign = "0"
        exponent = "0" * 11
        mantissa = "0" * 52
    return {"sign": sign, "exponent": exponent, "mantissa": mantissa}


def draw_floating_point_number(n_bits, input_width, ftype="float"):
    # Convert the number to binary representation
    binary_rep = float_to_binary(ftype=ftype)
    sign = binary_rep["sign"]
    exponent = binary_rep["exponent"]
    mantissa = binary_rep["mantissa"]

    # Determine the number of bits to color and the opacity
    n_whole_bits = int(n_bits)
    opacity = (n_bits - n_whole_bits) / 2 + 0.5

    # Estimate the required width of the plot figure
    plot_width = input_width / 100  # 100 is a scaling factor

    # Create a figure with Matplotlib, adjusting size to match input image
    fig, ax = plt.subplots(
        figsize=(plot_width, 0.4), dpi=330
    )  # High DPI for better resolution
    ax.axis("off")

    bit_width = 0.01  # Width of each bit
    bit_height = 0.5  # Height of each bit

    # Function to draw a rectangle for a bit with a black border
    def draw_bit(ax, x, y, color, opacity=1.0):
        rect = plt.Rectangle(
            (x, y),
            bit_width,
            bit_height,
            edgecolor="black",
            facecolor=color,
            alpha=opacity,
            linewidth=1,
        )
        ax.add_patch(rect)

    # Draw rectangles for each bit
    x = 0.01  # Starting position
    draw_bit(ax, x, 0.5, "white", opacity=0.5)  # Sign bit
    x += bit_width

    for bit in exponent:  # Exponent bits
        draw_bit(ax, x, 0.5, "tab:orange", opacity=0.5)
        x += bit_width

    for i, bit in enumerate(mantissa):  # Mantissa bits
        color = "tab:blue" if i < n_whole_bits else "red"
        opac = opacity if i == n_whole_bits else 1
        draw_bit(ax, x, 0.5, color, opac)

        x += bit_width

    # Save the plot to a temporary image file
    temp_file = tempfile.NamedTemporaryFile(suffix=".png")
    plt.savefig(temp_file.name, bbox_inches="tight")
    plt.close(fig)
    return temp_file


def get_text_image(text, input_width):
    # Create an image for the text annotations
    text_img = Image.new("RGB", (input_width, 50), color="white")
    draw = ImageDraw.Draw(text_img)
    # font = ImageFont.load_default()
    font = ImageFont.truetype("/usr/share/fonts/truetype/freefont/FreeMono.ttf", 25)

    # Add text annotations
    draw.text((10, 10), text, fill="black", font=font)

    return text_img


def paste_image_below(image, to_paste, x, y, mask=None):
    image.paste(to_paste, (x, y), mask=mask)
    new_height = y + to_paste.height
    return new_height


def create_frame(input_figure, i):
    # Load the input figure to determine its size
    input_image = Image.open(input_figure)
    input_width, input_height = input_image.size

    # Load statistics
    z, mean, std, sigbits, sigdigits = np.loadtxt(f"{input_figure}.txt")

    temp_file = draw_floating_point_number(sigbits, input_width)

    # Open the saved plot
    plot_image = Image.open(temp_file.name)

    # Add text annotations
    alignment = "    "
    z_text = alignment + f"z = {z:.7f}"
    z_img = get_text_image(z_text, input_width)

    text = alignment + f"T(z) = {mean:-.7f} ± {std:.3e}"
    mean_std_img = get_text_image(text, input_width)

    sigdigits_text = alignment + f"Significant digits: {sigdigits:4.2f}"
    sigdigits_img = get_text_image(sigdigits_text, input_width)

    sigbits_text = alignment + f"Significant bits:   {sigbits:>4.2f}"
    sigbits_img = get_text_image(sigbits_text, input_width)

    new_height = sum(
        x.height
        for x in [
            input_image,
            z_img,
            mean_std_img,
            sigdigits_img,
            sigbits_img,
            plot_image,
        ]
    )

    # Combine images
    combined_image = Image.new("RGBA", (input_width, new_height))

    next_height = 0
    next_height = paste_image_below(combined_image, input_image, 0, next_height)
    next_height = paste_image_below(combined_image, z_img, 0, next_height)
    next_height = paste_image_below(combined_image, mean_std_img, 0, next_height)
    next_height = paste_image_below(combined_image, sigdigits_img, 0, next_height)
    next_height = paste_image_below(combined_image, sigbits_img, 0, next_height)
    next_height = paste_image_below(
        combined_image, plot_image, 0, next_height, mask=plot_image
    )

    # Save the combined frame
    # combined_image.save(f"frame_{i}.png")
    temp_file.close()
    return combined_image


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-directory", type=str, default="frames", help="The output file"
    )
    parser.add_argument(
        "--input-directory", type=str, default="output_images", help="The input file"
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    input_images = sorted(
        glob.glob(f"{args.input_directory}/*.jpg"), key=natural_sort_key
    )
    for i, input_image in tqdm.tqdm(enumerate(input_images), total=len(input_images)):
        output_path = os.path.join(args.output_directory, f"frame_{i}.png")
        frame = create_frame(input_image, i)
        frame.save(output_path)


if __name__ == "__main__":
    main()
