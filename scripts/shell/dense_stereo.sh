#!/bin/sh

echo "COLMAP: DENSE RECONSTRUCTION: STEREO"
echo "WORKSPACE PATH:" $1

colmap dense_stereo \
--workspace_path $1

echo "STEREO COMPLETE"
exit
