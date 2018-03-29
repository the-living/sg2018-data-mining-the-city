#!/bin/sh

echo "COLMAP: AUTOMATIC RECONSTRUCTION"
echo "WORKING DIRECTORY:"$1

WORKING_PATH=$1

colmap automatic_reconstructor \
--workspace_path $WORKING_PATH \
--image_path $WORKING_PATH/images \
--camera_model OPENCV_FISHEYE \
--single_camera 1

echo "AUTOMATIC RECONSTRUCTION COMPLETE"
exit
