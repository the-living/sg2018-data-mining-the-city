#!/bin/sh
echo "COLMAP: DENSE - FUSION"
echo "WORKING DIRECTORY:" $1

WORKING_PATH = $1

colmap dense_fuser \
    --workspace_path $WORKING_PATH/dense \
    --workspace_format COLMAP \
    --input_type geometric \
    --output_path $WORKING_PATH/dense.fused.ply

echo "DENSE FUSION COMPLETE"
echo 1
