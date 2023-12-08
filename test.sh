#!/bin/bash
set -e

# required so that seq behaves correctly in all locales
export LC_ALL=C

# Compile tchebychev.c using MCA lib instrumentation

# Tchebychev polynom becomes unstable around 1, when computed with
# single precision
export VFC_BACKENDS="libinterflop_mca.so --precision-binary32 23"
export VFC_BACKENDS_SILENT_LOAD="True"
export VFC_BACKENDS_LOGGER="False"

verificarlo-c tchebychev.c -o tchebychev

rm -f output

# Run 15 iterations of tchebychev for all values in [.0:1.0:.01]
echo -e "z y" >> output
parallel -k -j $(nproc) --header : "for i in {1..15} ; do ./tchebychev {z} ; done" ::: z $(seq 0 0.001 1.0) >>output

mkdir -p frames output_images

# Decrease the resolution to be faster
echo "Plotting the results"
python3 plot.py --resolution 0.25

echo "Generating the frames"
python3 generate_frames.py

echo "Generating the gif"
python3 make_gif.py --directory frames --output tchebychev.gif --input-regexp='*.png' --duration 0.1