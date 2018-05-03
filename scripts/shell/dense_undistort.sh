#!/bin/sh

echo "COLMAP: DENSE RECONSTRUCTION: UNDISTORTION"

echo "IMAGE PATH:" $1
echo "MODEL PATH:" $2
echo "OUTPUT PATH:" $3

colmap image_undistorter \
--image_path $1 \
--input_path $2 \
--output_path $3

echo "UNDISTORTION COMPLETE"
exit
