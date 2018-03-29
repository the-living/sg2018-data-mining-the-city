#!/bin/sh

echo "COLMAP: EXHAUSTIVE MATCHING"
echo "WORKING DIRECTORY:" $1

WORKING_PATH=$1

colmap exhaustive_matcher \
--database_path $WORKING_PATH/database.db

echo "EXHAUSTIVE MATCHING COMPLETE"
exit
