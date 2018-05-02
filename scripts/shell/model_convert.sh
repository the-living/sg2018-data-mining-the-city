#!/bin/sh

echo "COLMAP: MODEL CONVERT"
echo "INPUT_PATH:" $1
echo "OUTPUT_PATH:" $2
echo "OUTPUT_TYPE:" $3

colmap model_merger \
--input_path $1 \
--output_path $2 \
--output_type $3

echo "MODEL MERGE COMPLETE"
exit
