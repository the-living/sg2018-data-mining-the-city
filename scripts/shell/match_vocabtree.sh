#!/bin/sh

echo "COLMAP: VOCAB TREE MATCHING"

WORKING_PATH=$1
VOCAB_TREE=$2

echo "WORKING DIRECTORY:" $WORKING_PATH
echo "VOCAB TREE" $VOCAB_TREE

colmap vocab_tree_matcher \
--database_path $WORKING_PATH/database.db \
--VocabTreeMatching.vocab_tree_path $VOCAB_TREE

echo "VOCAB TREE MATCHING COMPLETE"
exit
