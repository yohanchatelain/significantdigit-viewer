# Import necessary libraries
import argparse
from turtle import st
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import os
import significantdigits as sd


def load_data(input):
    # Read the data from the file
    data = pd.read_csv(
        input, sep=" ", dtype=np.float64
    )  # Assuming the file is tab-separated
    return data


def downsample_array(arr, num_samples):
    # Calculate the step size. Use integer division for whole number steps
    step = len(arr) // num_samples

    # Use slicing to downsample
    downsampled_arr = arr[::step]

    # Ensure the downsampled array has the desired number of samples
    return downsampled_arr[:num_samples]


def create_figure(data, threshold=0.5):
    # remove the rows with z > threshold
    data = data[data["z"] <= threshold]

    # Create a scatter plot using Plotly
    fig = px.scatter(data, x="z", y="y", title="T(z)", opacity=0.5)
    fig.update_yaxes(range=[-3.5, 3.5])
    fig.update_xaxes(range=[0, 1])
    fig.update_layout(template="plotly_white", font=dict(size=18))
    return fig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="output", help="The input file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=1,
        help="The threshold for the plot",
    )
    parser.add_argument(
        "--resolution",
        type=float,
        default=0.1,
        help="Downsample the number of images by this factor",
    )
    parser.add_argument(
        "--output", type=str, default="output.jpg", help="The output file"
    )
    parser.add_argument(
        "--directory", type=str, default="output_images", help="The output directory"
    )
    return parser.parse_args()


def write_stats(data, threshold, output_filename):
    # remove the rows with z > threshold
    data = data[data["z"] <= threshold]
    # Get all values where z = max(z)
    z = data["z"].max()
    z_max = data[data["z"] == z]
    # Get statistics
    mean = z_max["y"].mean()
    std = z_max["y"].std()
    sigbits = sd.significant_digits(z_max["y"].values, reference=mean)
    sigdigts = sd.change_basis(sigbits, 10)

    with open(output_filename, "w") as f:
        msg = f"{z} {mean} {std} {sigbits} {sigdigts}"
        f.write(f"{msg}\n")


def process_threshold(data, i, threshold, output, directory):
    fig = create_figure(
        data, threshold=threshold
    )  # Assuming create_figure is predefined
    stats_output = os.path.join(directory, f"{i}_{output}.txt")
    write_stats(data, threshold, stats_output)
    path = os.path.join(directory, f"{i}_{output}")
    fig.write_image(path, width=1200, height=800)


def main():
    args = parse_args()
    data = load_data(args.input)

    assert 1 >= args.resolution > 0

    unique_z = data["z"].unique()
    z = downsample_array(unique_z, int(unique_z.size * args.resolution))

    print("Creating plots...")
    joblib.Parallel(n_jobs=-1, verbose=5)(
        joblib.delayed(process_threshold)(
            data, i, threshold, args.output, args.directory
        )
        for i, threshold in enumerate(z)
    )


if __name__ == "__main__":
    main()
