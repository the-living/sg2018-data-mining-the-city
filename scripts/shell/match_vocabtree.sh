#!/bin/sh

echo "COLMAP: VOCAB TREE MATCHING"
echo "WORKING DIRECTORY:" $1
echo "VOCAB TREE" $2

WORKING_PATH=$1
VOCAB_TREE=$2

colmap exhaustive_matcher \
--database_path $WORKING_PATH/database.db
--VocabTreeMatching.vocab_tree_path $VOCAB_TREE

echo "VOCAB TREE MATCHING COMPLETE"
exit
