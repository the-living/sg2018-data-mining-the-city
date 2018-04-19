#!/bin/sh

echo "COLMAP: MODEL MERGE"
echo "MODEL1_PATH:" $1
echo "MODEL2_PATH:" $2
echo "MERGE_PATH:" $3

colmap model_merger \
--input_path1 $1 \
--input_path2 $2 \
--output_path $3

echo "MODEL MERGE COMPLETE"
exit
