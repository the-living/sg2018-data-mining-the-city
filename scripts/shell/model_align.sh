#!/bin/sh

echo "COLMAP: MODEL ALIGNER"
echo "IMAGE_PATH:" $1
echo "INPUT_PATH:" $2
echo "OUTPUT_PATH:" $3

colmap model_orientation_aligner \
--image_path $1 \
--input_path $2 \
--output_path $3 \
--method MANHATTAN-WORLD

echo "MODEL ALIGNMENT COMPLETE"
exit
