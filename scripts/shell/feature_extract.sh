#!/bin/sh

echo "COLMAP: EXTRACT FEATURES"
echo "WORKING DIRECTORY:" $1
echo "CAMERA MODEL:" $2
echo "CAMERA INTRINSICS:" $3

WORKING_PATH=$1

colmap feature_extractor \
--database_path $WORKING_PATH/database.db \
--image_path $WORKING_PATH/images \
--ImageReader.camera_model $2 \
--ImageReader.single_camera 1 \
--ImageReader.camera_params $3

echo "FEATURE EXTRACTION COMPLETE"
exit
