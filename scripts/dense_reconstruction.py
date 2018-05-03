import os
# import cv2
# import json, math
# from glob import glob
import subprocess, shlex
from helpers import Timer, LogWriter

recon_settings = {
    "SCRIPT_DIR": "/home/living/Dropbox/recon_FINAL/scripts",
    "WORK_DIR": "/home/living/Dropbox/recon_FINAL/test_03",
    "IMAGE_DIR": "images",
    "MODEL_DIR": "final",
    "OUTPUT_DIR": "dense",

    "SKIP_UNDISTORT": False,
    "SKIP_STEREO": False,
    "SKIP_FUSION": False,
}

def reconstruct(settings):
    timer_global = Timer()

    SKIP_UNDISTORT = settings["SKIP_UNDISTORT"]
    SKIP_STEREO = settings["SKIP_STEREO"]
    SKIP_FUSION = settings["SKIP_FUSION"]

    # VALIDATE PATHS
    SCRIPT_DIR = settings["SCRIPT_DIR"].rstrip("/")
    assert os.path.exists(SCRIPT_DIR), "ERROR: SCRIPT PATH MISSING AT {}".format(SCRIPT_DIR)

    WORK_DIR = settings["WORK_DIR"].rstrip("/")
    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)

    IMAGE_DIR = settings["IMAGE_DIR"]
    IMAGE_DIR = "{}/{}".format(WORK_DIR, IMAGE_DIR)
    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    MODEL_DIR = settings["MODEL_DIR"]
    MODEL_DIR = "{}/{}".format(WORK_DIR, MODEL_DIR)
    if not os.path.exists(MODEL_DIR):
        os.mkdir(MODEL_DIR)

    OUTPUT_DIR = settings["OUTPUT_DIR"]
    OUTPUT_DIR = "{}/{}".format(WORK_DIR, OUTPUT_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    log = LogWriter(WORK_DIR)
    log.heading("DENSE RECONSTRUCTION")

    log.log("Undistorting images...")
    if not SKIP_UNDISTORT:
        timer = Timer()

        raw_input = "{}/shell/dense_undistort.sh {} {} {}".format(SCRIPT_DIR, IMAGE_DIR, MODEL_DIR, OUTPUT_DIR)
        args = shlex.split(raw_input)
        p = subprocess.Popen(args)
        p.wait()

        log.log("...complete ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")


    log.log("Stereo reconstruction...")
    if not SKIP_STEREO:
        timer = Timer()

        raw_input = "{}/shell/dense_stereo.sh {}".format(SCRIPT_DIR, OUTPUT_DIR)
        args = shlex.split(raw_input)
        p = subprocess.Popen(args)
        p.wait()

        log.log("...complete ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")


    log.log("Dense fusion...")
    if not SKIP_FUSION:
        timer = Timer()

        raw_input = "{}/shell/dense_fusion.sh {}".format(SCRIPT_DIR, OUTPUT_DIR)
        args = shlex.split(raw_input)
        p = subprocess.Popen(args)
        p.wait()

        log.log("...complete ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    log.log("\n...job finished ({} sec).".format(timer_global.read()))

if __name__ == "__main__":
    reconstruct(recon_settings)
