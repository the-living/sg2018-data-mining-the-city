#!/bin/sh

echo "COLMAP: DENSE RECONSTRUCTION: FUSION"
echo "WORKSPACE PATH:" $1

colmap dense_fuser \
--workspace_path $1 \
--output_path $1/fused.ply

echo "FUSION COMPLETE"
exit
