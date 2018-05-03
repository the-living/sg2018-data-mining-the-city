#!/bin/sh

echo "COLMAP: SPARSE RECONSTRUCTION"
echo "WORKING DIRECTORY:" $1
echo "MODEL PATH:" $2

WORKING_PATH=$1

colmap mapper \
--database_path $WORKING_PATH/database.db \
--image_path $WORKING_PATH/images \
--export_path $WORKING_PATH/sparse/$2 \
--image_list_path $WORKING_PATH/image_list.txt \
--Mapper.ba_refine_focal_length 0 \
--Mapper.ba_refine_extra_params 0 \
--Mapper.ignore_watermarks 1
# --Mapper.ba_global_images_ratio 1.2 \       # speed up bundle adjustment
# --Mapper.ba_global_points_ratio 1.2 \       # speed up bundle adjustment
# --Mapper.ba_global_max_num_iterations 20 \  # speed up bundle adjustment
# --Mapper.ba_global_max_refinements 3 \      # speed up bundle adjustment
# --Mapper.ba_global_points_freq 200000 \     # speed up bundle adjustment
# --Mapper.init_image_id1 -1 \
# --Mapper.init_image_id2 -1 \
# --Mapper.abs_pose_max_error 4.0 \
# --Mapper.abs_pose_min_num_inliers 10 \
# --Mapper.abs_pose_min_inlier_ratio 0.10 \
# --Mapper.max_reg_trials 8

echo "SPARSE RECONSTRUCTION COMPLETE"
exit
