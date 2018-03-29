#!/bin/sh
echo "COLMAP: DENSE - COMPUTE STEREO"
echo "WORKING DIRECTORY:" $1

WORKING_PATH = $1

colmap dense_stereo \
    --workspace_path $WORKING_PATH/dense \
    --workspace_format COLMAP \
    --DenseStereo.geom_consistency true

echo "DENSE STEREO COMPLETE"
echo 1
