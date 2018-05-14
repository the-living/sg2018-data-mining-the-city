import cv2
import numpy as np
from colmap_read_dense import read_array
from matplotlib import cm
from glob import glob

# POINT TO DIRECTORIES CONTAINING DENSE .BIN FILES
DEPTH_DIR = "vis/model/dense/depth"
NORM_DIR = "vis/model/dense/normal"

# POINT TO DIRECTORIES WHERE OUTPUT JPGS WILL BE SAVED
DEPTH_OUT = "vis/model/dense_raster/depth"
NORM_OUT = "vis/model/dense_raster/normal"

def gen_depthmap(a):
    depth = read_array(a)
    # CLAMP DEPTH VALUES
    min_depth, max_depth = np.percentile(depth,[5,95])
    depth = np.clip(depth,min_depth,max_depth)
    depth -= min_depth
    if (max_depth-min_depth) != 0:
        depth /= (max_depth-min_depth)
    return cv2.cvtColor(np.uint8(cm.plasma(depth)*255),cv2.COLOR_RGB2BGR)

def gen_normmap(a, bg_override=None):
    norm = read_array(a)
    # SHIFT ARRAY VALUES FROM (-1,1) TO (0,1)
    norm += 1
    norm *= 0.5
    # BACKGROUND OVERRIDE
    if bg_override:
        norm[np.where((norm==[0.5,0.5,0.5]).all(axis=2))] = bg_override
    norm *= 255
    # CONVERT FROM RGB COLORSPACE TO BGR (CV)
    return cv2.cvtColor(np.uint8(norm), cv2.COLOR_RGB2BGR)

def process(output_depth=True, output_normal=True, geometric_only=True):
    if output_depth:
        depths = glob("{}/*.geometric.bin".format(DEPTH_DIR)) if geometric_only \
            else glob("{}/*.bin".format(DEPTH_DIR))
        for d in depths:
            filename = d.split('/')[-1].split('.')[0] + ".jpg"
            outpath = "{}/{}".format(DEPTH_OUT, filename)
            cv2.imwrite(outpath, gen_depthmap(d))

    if output_normal:
        norms = glob("{}/*.geometric.bin".format(NORM_DIR)) if geometric_only \
            else glob("{}/*.bin".format(NORM_DIR))
        for n in norms:
            filename = n.split('/')[-1].split('.')[0] + ".jpg"
            outpath = "{}/{}".format(NORM_OUT, filename)
            cv2.imwrite(outpath, gen_normmap(n))

if __name__ == "__main__":
    process(output_depth=True, output_normal=True, geometric_only=True)
