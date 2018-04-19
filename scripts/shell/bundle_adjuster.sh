#!/bin/sh

echo "COLMAP: BUNDLE ADJUSTMENT"
echo "MODEL_PATH:" $1\

colmap bundle_adjuster \
--input_path $1 \
--output_path $1

echo "BUNDLE ADJUSTMENT COMPLETE"
exit
