#!/bin/sh
echo "COLMAP: DENSE - MESHING"
echo "WORKING DIRECTORY:" $1

WORKING_PATH = $1

colmap dense_mesher \
    --input_path $WORKING_PATH/dense/fused.ply \
    --output_path $WORKING_PATH/dense/meshed.ply

echo "DENSE MESHING COMPLETE"
echo 1
