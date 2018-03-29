#!/bin/sh

echo "COLMAP: IMPORT FEATURES"
echo "WORKING DIRECTORY:"$1

WORKING_PATH=$1

colmap feature_importer \
--database_path $WORKING_PATH/database.db \
--image_path $WORKING_PATH/images \
--import_path $WORKING_PATH/images \
--ImageReader.camera_model OPENCV_FISHEYE \
--ImageReader.single_camera 1

echo "FEATURE IMPORT COMPLETE"
