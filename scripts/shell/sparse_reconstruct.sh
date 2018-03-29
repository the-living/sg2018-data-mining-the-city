#!/bin/sh

echo "COLMAP: SPARSE RECONSTRUCTION"
echo "WORKING DIRECTORY:" $1

WORKING_PATH=$1

colmap mapper \
--database_path $WORKING_PATH/database.db \
--image_path $WORKING_PATH/images \
--export_path $WORKING_PATH/sparse

echo "SPARSE RECONSTRUCTION COMPLETE"
exit
