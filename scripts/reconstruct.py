import os
import cv2
import json
from glob import glob
import subprocess, shlex
from helpers import VideoExtractor, SIFTExtractor

recon_settings = {
    "VERBOSE": True,
    "WORK_DIR": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/work_folder_presift",
    "SCRIPT_DIR": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/scripts",

    "SKIP_LOAD": True,
    "SKIP_RECONSTRUCT": False,

    "FRONT_VIDEO": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/V0090016.MP4",
    "BACK_VIDEO": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/V0090017.MP4",

    "FRONT_MASK": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/mask_front_basic.png",
    "BACK_MASK": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/mask_back_basic.png",

    "TIME_START": 2,
    "TIME_END": 42,
    "TIME_INTERVAL": 1,

    "IMAGE_DIR": "images",
    "IMAGE_SCALE": 1,
    "PROCESS_SIFT": True,
    "SAVE_SIFT": True,
    "SIFT_DIR": "sift_output",

    "EXIF_REF": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/ref_img.JPG",
    "FIT_REF": "/home/tl-admin/Dropbox/TL_WORKING/SmartGeometry/stack_test/inputs/2018-03-19-09-24-10.fit"
}

# reconstruct_script="~/Dropbox/TL_WORKING/SmartGeometry/stack_test/scripts/reconstruct.sh"

def build_reconstruction(settings):
    # LOAD SETTINGS
    # f = open(fp, mode='r')
    # settings = json.load(f)
    # f.close()

    # GENERATE INPUTS & CHECK VALIDITY
    VERBOSE = settings["VERBOSE"]
    if VERBOSE:
        print("RUNNING IN VERBOSE MODE\n\n")

    SKIP_LOAD = settings["SKIP_LOAD"]
    SKIP_RECONSTRUCT = settings["SKIP_RECONSTRUCT"]

    # WORK DIRECTORY
    WORK_DIR = settings["WORK_DIR"].rstrip("/")
    SCRIPT_DIR = settings["SCRIPT_DIR"].rstrip("/")
    assert os.path.exists(SCRIPT_DIR), "ERROR: SCRIPT PATH MISSING AT {}".format(SCRIPT_DIR)

    IMAGE_DIR = settings["IMAGE_DIR"].rstrip("/")
    IMAGE_DIR = "{}/{}".format(WORK_DIR, IMAGE_DIR)
    PROCESS_SIFT = settings["PROCESS_SIFT"]
    SAVE_SIFT = settings["SAVE_SIFT"]
    SIFT_DIR = settings["SIFT_DIR"].rstrip("/")
    SIFT_DIR = "{}/{}".format(WORK_DIR, SIFT_DIR)
    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)
    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)
    if PROCESS_SIFT:
        if not os.path.exists(SIFT_DIR) and SAVE_SIFT:
            os.mkdir(SIFT_DIR)

    if not SKIP_LOAD:
        # INPUT VIDEOS
        FRONT_VIDEO = settings["FRONT_VIDEO"]
        assert os.path.exists(FRONT_VIDEO), "ERROR: FRONT VIDEO MISSING AT {}".format(FRONT_VIDEO)
        BACK_VIDEO = settings["BACK_VIDEO"]
        assert os.path.exists(BACK_VIDEO), "ERROR: BACK VIDEO MISSING AT {}".format(BACK_VIDEO)

        # IMAGE SCALE SETTINGS
        IMAGE_SCALE = settings["IMAGE_SCALE"]

        # INPUT MASKS
        if PROCESS_SIFT:
            assert os.path.exists(settings["FRONT_MASK"]), "ERROR: FRONT MASK MISSING AT {}".format(settings["FRONT_MASK"])
            FRONT_MASK = cv2.imread(settings["FRONT_MASK"])
            FRONT_MASK = cv2.cvtColor(FRONT_MASK,cv2.COLOR_BGR2GRAY)
            assert os.path.exists(settings["BACK_MASK"]), "ERROR: BACK MASK MISSING AT {}".format(BACK_MASK)
            BACK_MASK = cv2.imread(settings["BACK_MASK"])
            BACK_MASK = cv2.cvtColor(BACK_MASK, cv2.COLOR_BGR2GRAY)
        if IMAGE_SCALE != 1:
            m_h,m_w = FRONT_MASK.shape[:2]
            FRONT_MASK = cv2.resize(FRONT_MASK, fx=IMAGE_SCALE, fy=IMAGE_SCALE, interpolation=cv2.INTER_NEAREST)
            BACK_MASK = cv2.resize(BACK_MASK, fx=IMAGE_SCALE, fy=IMAGE_SCALE, interpolation=cv2.INTER_NEAREST)

        # VIDEO TIME SETTINGS
        TIME_START = int(settings["TIME_START"])
        TIME_END = int(settings["TIME_END"])
        TIME_INTERVAL = int(settings["TIME_INTERVAL"])

        # EXIF TEMPLATE
        EXIF_REF = settings["EXIF_REF"]
        assert os.path.exists(EXIF_REF), "ERROR: EXIF REF MISSING AT {}".format(EXIF_REF)
        # FIT FILE
        FIT_REF = settings["FIT_REF"]
        assert os.path.exists(FIT_REF), "ERROR: FIT REF MISSING AT {}".format(FIT_REF)

        # - - - - - - - - - - #
        # - - - - - - - - - - #
        # - - - - - - - - - - #

        # CREATE FRAME EXTRACTOR OBJECT
        extractor = VideoExtractor(FRONT_VIDEO, BACK_VIDEO, FIT_REF, EXIF_REF, IMAGE_SCALE)
        sifter = SIFTExtractor()

        # ITERATE THROUGH FRAMES
        frame_data = {}
        if VERBOSE:
            print("EXTRACTING FRAMES:\nSTART: {} sec\nEND: {} sec\nINTERVAL: {} sec\n\n").format(TIME_START, TIME_END, TIME_INTERVAL)
        for t in xrange(TIME_START, TIME_END, TIME_INTERVAL):
            front_file = "front_%05d.jpg" % (t)
            back_file = "back_%05d.jpg" % (t)

            front, back, record = extractor.extract(t)
            if front is None or back is None:
                continue

            if VERBOSE:
                print("GENERATING FRAMES @ {} sec".format(t))

            frame_data[front_file] = record

            front_path = "{}/{}".format(IMAGE_DIR, front_file)
            back_path = "{}/{}".format(IMAGE_DIR, back_file)

            cv2.imwrite(front_path, front)
            cv2.imwrite(back_path, back)

            extractor.writeEXIF(front_path, back_path, record)

            if PROCESS_SIFT:
                kpA, desA = sifter.process(front, FRONT_MASK, SAVE_SIFT)
                kpB, desB = sifter.process(back, BACK_MASK, SAVE_SIFT)

                sifter.saveTXT(kpA, desA, front_path)
                sifter.saveTXT(kpB, desB, back_path)

                if VERBOSE:
                    print ("FRONT / {} keypoints x {} descriptors".format(*desA.shape))
                    print ("BACK / {} keypoints x {} descriptors".format(*desB.shape))

                if SAVE_SIFT:
                    front_kp_path = "{}/{}.kp.jpg".format(SIFT_DIR, front_file)
                    back_kp_path = "{}/{}.kp.jpg".format(SIFT_DIR, back_file)
                    cv2.imwrite(front_kp_path, sifter.label(front, kpA, copy=True, gray=True))
                    cv2.imwrite(back_kp_path, sifter.label(back, kpB, copy=True, gray=True))

            if VERBOSE:
                print("\n")

        # SAVE FRAME DATA
        f = open("{}/image_data.json".format(WORK_DIR), mode='w')
        json.dump(frame_data, f, sort_keys=True, indent=4, separators=(',', ': '))
        f.close()

    if not SKIP_RECONSTRUCT:
        if os.path.exists("{}/database.db".format(WORK_DIR)):
            os.remove("{}/database.db".format(WORK_DIR))

        if VERBOSE:
            if not PROCESS_SIFT:
                print("COLMAP: AUTOMATIC RECONSTRUCTION\n\n")
            else:
                print("COLMAP: RECONSTRUCTION\n\n")

        img_count = glob("{}/*.jpg".format(IMAGE_DIR))
        VOCAB_TREE = "{}/vocab_tree/vocab_tree-{}.bin".format(SCRIPT_DIR, 65536 if len(img_count)<1000 else 262144)

        # IF NOT USING IMPORTED SIFT FEATURES, USE AUTOMATIC RECONSTRUCTION SCRIPT
        if not PROCESS_SIFT:
            raw_input = "{}/shell/automatic_reconstruction.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)

            p = subprocess.Popen(args)

            p.wait()
        else:
            if not os.path.exists("{}/sparse".format(WORK_DIR)):
                os.mkdir("{}/sparse".format(WORK_DIR))
            if not os.path.exists("{}/dense".format(WORK_DIR)):
                os.mkdir("{}/dense".format(WORK_DIR))

            # IMPORT FEATURES
            if VERBOSE:
                print("\n\nIMPORTING FEATURES\n\n")
            raw_input = "{}/shell/feature_import.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            # print args
            p = subprocess.Popen(args)
            p.wait()

            # EXHAUSTIVE MATCH
            if VERBOSE:
                print("\n\nMATCHING FEATURES - EXHAUSTIVE\n\n")
            raw_input = "{}/shell/match_exhaustive.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            out,err = p.communicate()
            if "ERROR" in out:
                if VERBOSE:
                    print("\n\nMATCHING FEATURES - VOCAB TREE\n\n")
                raw_input = "{}/shell/match_vocabtree.sh {} {}".format(SCRIPT_DIR, WORK_DIR, VOCAB_TREE)
                args = shlex.split(raw_input)
                # print args
                p = subprocess.Popen(args, stdout=subprocess.PIPE)
                out, err = p.communicate()
                if "ERROR" in out:
                    if VERBOSE:
                        print("\n\nNOT ENOUGH GPU MEMORY, QUITTING RECONSTRUCTION\n\n")
                    return

                    if VERBOSE:
                        print("\n\nNOT ENOUGH GPU MEMORY, RUNNING AUTOMATIC RECONSTRUCTION\n\n")
                    os.remove("{}/database.db".format(WORK_DIR))
                    os.rmdir("{}/sparse".format(WORK_DIR))
                    os.rmdir("{}/dense".format(WORK_DIR))
                    raw_input = "{}/shell/automatic_reconstruction.sh {}".format(SCRIPT_DIR, WORK_DIR)
                    args = shlex.split(raw_input)
                    # print args
                    p = subprocess.Popen(args)
                    # out,err = p.communicate()
                    p.wait()
                    return

            # RECONSTRUCT SPARSE
            raw_input = "{}/shell/sparse_reconstruct.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            print args
            p = subprocess.Popen(args)
            p.wait()

            # DENSE - UNDISTORT
            raw_input = "{}/shell/dense_undistort.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            # print args
            p = subprocess.Popen(args)
            p.wait()

            # DENSE - STEREO
            raw_input = "{}/shell/dense_stereo.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            # print args
            p = subprocess.Popen(args)
            p.wait()

            # DENSE - FUSION
            raw_input = "{}/shell/dense_fuse.sh {}".format(SCRIPT_DIR, WORK_DIR)
            args = shlex.split(raw_input)
            # print args
            p = subprocess.Popen(args)
            p.wait()

            # DENSE - MESHING
            raw_input = "{}/shell/dense_mesh.sh {}".format(SCRIPT_DIR, WORK_DIR)
            p = subprocess.Popen(shlex.split(raw_input))
            p.wait()



    # IMPORT FEATURES INTO COLMAP
    # if VERBOSE:
    #     print("COLMAP: IMPORTING IMAGE FEATURES\n\n")
    # args = [
    #     "colmap feature_importer",
    #     "--database_path {}/database.db".format(WORK_DIR),
    #     "--image_path {}".format(IMAGE_DIR),
    #     "--import_path {}".format(IMAGE_DIR),
    #     "--ImageReader.camera_model OPENCV_FISHEYE",
    #     "--ImageReader.single_camera 1"]
    # call(args, shell=True)
    # #
    # # EXHAUSTIVE MATCHING
    # if VERBOSE:
    #     print("COLMAP: IMAGE FEATURES MATCHING [EXHAUSTIVE]\n\n")
    # args = [
    #     "colmap exhaustive_matcher",
    #     "--database_path {}/database.db".format(WORK_DIR)]
    # call(args, shell=True)
    #
    # # RECONSTRUCT SPARSE MODEL
    # if VERBOSE:
    #     print("COLMAP: RECONSTRUCTING SPARE MODEL\n\n")
    # os.mkdir("{}/sparse".format(WORK_DIR))
    # args = [
    #     "colmap mapper",
    #     "--database_path {}/database.db".format(WORK_DIR),
    #     "--image_path {}".format(IMAGE_DIR),
    #     "--export_path {}/sparse".format(WORK_DIR)]
    # call(args, shell=True)
    #
    # # DENSE: UNDISTORT IMAGES
    # if VERBOSE:
    #     print("COLMAP: DENSE - UNDISTORT IMAGES\n\n")
    # os.mkdir("{}/dense".format(WORK_DIR))
    # args = [
    #     "colmap image_undistorter",
    #     "--image_path {}".format(IMAGE_DIR),
    #     "--input_path {}/sparse/0".format(WORK_DIR),
    #     "--output_path {}/dense".format(WORK_DIR),
    #     "--output_type COLMAP",
    #     "--max_image_size 2000"]
    # call(args, shell=True)
    #
    # # DENSE: STEREO RECONSTRUCTION
    # if VERBOSE:
    #     print("COLMAP: DENSE - BUILDING STEREO\n\n")
    # args = [
    #     "colmap dense_stereo",
    #     "--workspace_path {}/dense".format(WORK_DIR),
    #     "--workspace_format COLMAP",
    #     "--DenseStereo.geom_consistency true"]
    # call(args, shell=True)
    #
    # # DENSE: FUSED RECONSTRUCTION
    # if VERBOSE:
    #     print("COLMAP: DENSE - FUSED\n\n")
    # args = [
    #     "colmap dense_fuser",
    #     "--workspace_path {}/dense".format(WORK_DIR),
    #     "--workspace_format COLMAP",
    #     "--input_type geometric",
    #     "--output_path {}/dense/fused.ply".format(WORK_DIR)]
    # call(args, shell=True)
    #
    # # DENSE: MESH FUSED
    # if VERBOSE:
    #     print("COLMAP: DENSE - MESHING\n\n")
    # args = [
    #     "colmap dense_mesher",
    #     "--input_path {}/dense/fused.ply".format(WORK_DIR),
    #     "--output_path {}/dense/meshed.ply".format(WORK_DIR)]
    # call(args, shell=True)
    # cmd = "{} {}".format(reconstruct_script, WORK_DIR)
    # print(cmd)
    # call(cmd, shell=True)

if __name__ == "__main__":
    build_reconstruction(recon_settings)
    print("\n\nCOMPLETE\n\n")
    exit()
