#!/bin/sh
echo "COLMAP: DENSE - IMAGE UNDISTORTION"
echo "WORKING DIRECTORY:" $1

WORKING_PATH = $1

colmap image_undistorter \
    --image_path $WORKING_PATH/images \
    --input_path $WORKING_PATH/sparse/0 \
    --output_path $WORKING_PATH/dense \
    --output_type COLMAP \
    --max_image_size 2000

echo "IMAGE UNDISTORTION COMPLETE"
echo 1
