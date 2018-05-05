import os
import cv2
import json, math
from glob import glob
import subprocess, shlex
from helpers import VideoExtractor, Timer, LogWriter, make_image_list, CameraTrackExtractor

recon_settings = {
    "SCRIPT_DIR": "/home/tl-admin/DEV/sg2018-data-mining-the-city/scripts",
    "WORK_DIR": "/home/tl-admin/DEV/SG_STACK/TEST_SPLIT",
    "IMAGE_DIR": "images",

    "SKIP_LOAD_IMAGES": True,
    "SKIP_FIND_FEATURES": True,
    "SKIP_FIND_MATCHES": True,
    "SKIP_RECONSTRUCT": True,
    "SKIP_MERGE": True,
    "SKIP_ALIGNMENT": False,
    "SKIP_SPARSE_CONVERT": False,


    "VIDEO_PATH": "/home/tl-admin/DEV/SG_STACK/TEST_SPLIT/inputs/03_360.mp4",

    # "TIME_START": 0,
    # "TIME_END": 200,
    "TIME_INTERVAL": 1.0,

    "FRAME_HEIGHT": 1080,
    "FRAME_WIDTH": 2160,
    "FRAME_FOV": 0.45,
    "FRAMES_PER_MODEL": 180,
    "MODEL_OVERLAP": 10,
    "IMAGE_SCALE": 1.0,

    #"CAMERA_MODEL": "RADIAL_FISHEYE",
    #"CAMERA_FOCAL_LENGTH": 720.0,
    #"CAMERA_PARAMS": [0.156447,0.0926909],
    "CAMERA_MODEL": "SIMPLE_PINHOLE",
    "CAMERA_FOCAL_LENGTH": 768.734764,
    "CAMERA_PARAMS": None,

    # "EXIF_REF": "/home/living/Dropbox/recon_test/inputs/ref_img-2.JPG",
    # "FIT_REF": "/home/tl-admin/DEV/SG_STACK/TEST_SPLIT/inputs/2018-03-19-09-24-10.fit"
}

def reconstruct(settings):
    timer_global = Timer()

    # LOAD SETTINGS
    SKIP_LOAD_IMAGES = settings["SKIP_LOAD_IMAGES"]
    SKIP_FIND_FEATURES = settings["SKIP_FIND_FEATURES"]
    SKIP_FIND_MATCHES = settings["SKIP_FIND_MATCHES"]
    SKIP_RECONSTRUCT = settings["SKIP_RECONSTRUCT"]
    SKIP_MERGE = settings["SKIP_MERGE"]
    SKIP_ALIGNMENT = settings["SKIP_ALIGNMENT"]
    SKIP_SPARSE_CONVERT = settings["SKIP_SPARSE_CONVERT"]

    # VALIDATE PATHS
    SCRIPT_DIR = settings["SCRIPT_DIR"].rstrip("/")
    assert os.path.exists(SCRIPT_DIR), "ERROR: SCRIPT PATH MISSING AT {}".format(SCRIPT_DIR)

    WORK_DIR = settings["WORK_DIR"].rstrip("/")
    if not os.path.exists(WORK_DIR):
        os.mkdir(WORK_DIR)

    IMAGE_DIR = "images"
    IMAGE_DIR = "{}/{}".format(WORK_DIR, IMAGE_DIR)
    if not os.path.exists(IMAGE_DIR):
        os.mkdir(IMAGE_DIR)

    FRAME_WIDTH = settings["FRAME_WIDTH"]
    FRAME_HEIGHT = settings["FRAME_HEIGHT"]
    if FRAME_WIDTH < 2 * FRAME_HEIGHT:
        FRAME_WIDTH = 2 * FRAME_HEIGHT
    FRAME_FOV = settings["FRAME_FOV"]
    IMAGE_SCALE = settings["IMAGE_SCALE"]


    # VIDEO TIME SETTINGS
    try:
        TIME_START = int(settings["TIME_START"])
        TIME_END = int(settings["TIME_END"])
    except KeyError:
        TIME_START = 0
        # TIME_END = int(math.floor(extractor.getEnd()))
        TIME_END = 600
    TIME_INTERVAL = settings["TIME_INTERVAL"]
    NUM_FRAMES = int(math.floor((TIME_END - TIME_START) / float(TIME_INTERVAL)))

    # GET PATHS TO VIDEOS
    # VIDEO_PATHS = [settings["VIDEO_PATH"] + path for path in settings["VIDEO_FILES"]]
    # for video in VIDEO_PATHS:
    #     assert os.path.exists(video), "ERROR: VIDEO MISSING AT {}".format(video)
    # VIDEO_PREFIX = settings["VIDEO_FILES"][0].split('_')[0]
    VIDEO_PATH = settings["VIDEO_PATH"]
    assert os.path.exists(VIDEO_PATH), "ERROR: VIDEO MISSING AT {}".format(VIDEO_PATH)
    VIDEO_PREFIX = VIDEO_PATH.split("/")[-1].split(".")[0]

    # FIT_REF = settings["FIT_REF"]
    # assert os.path.exists(FIT_REF), "ERROR: FIT REF MISSING AT {}".format(FIT_REF)

    if not SKIP_LOAD_IMAGES or not SKIP_FIND_FEATURES:
        # CREATE FRAME EXTRACTOR OBJECT
        print("\nLOADING VIDEOS... {}".format(VIDEO_PATH))
        extractor = VideoExtractor(
            VIDEO_PATH,
            # FIT_REF,
            IMAGE_SCALE,
            frame_width=FRAME_WIDTH,
            frame_height=FRAME_HEIGHT,
            fov=FRAME_FOV
            )

    log = LogWriter(WORK_DIR)

    # # # # # # # # #
    # IMAGE LOADING #
    # # # # # # # # #
    log.heading("IMAGE LOADING")

    if not SKIP_LOAD_IMAGES:
        timer = Timer()

        log.log("Using video:")
        # for path in VIDEO_PATHS:
        #     log.log(path)
        log.log(VIDEO_PATH.split("\\")[-1])

        # ITERATE THROUGH FRAMES
        # frame_data = {}
        subflag = "NESW"

        print("\nEXTRACTING FRAMES:\nSTART: {} sec\nEND: {} sec\nINTERVAL: {} sec\n").format(TIME_START, TIME_END, TIME_INTERVAL)

        img_counter = 0
        for frame in range(NUM_FRAMES):

            frame_ID = "{:05d}".format(frame)

            t = TIME_START + frame*TIME_INTERVAL
            # data = extractor.extract(t)
            # frames = data[:-1]
            # record = data[-1]
            frames = extractor.extract(t)
            if frames is None:
                continue

            file_names = ["{}_{}_{}.jpg".format(VIDEO_PREFIX, subflag[i], frame_ID) for i in xrange(len(frames))]

            print("GENERATING FRAMES @ {} sec".format(t))

            # frame_data[frame_ID] = record

            file_paths = ["{}/{}".format(IMAGE_DIR, file_name) for file_name in file_names]

            for i,file_path in enumerate(file_paths):
                # print file_path
                cv2.imwrite(file_path, frames[i])
                img_counter += 1

            # if exif_exists:
                # extractor.writeEXIF(file_paths, record)

        # SAVE FRAME DATA
        # with open("{}/image_data.json".format(WORK_DIR), mode='w') as f:
        #     json.dump(frame_data, f, sort_keys=True, indent=4, separators=(',', ': '))

        log.log("Successfully loaded {} images ({} sec)".format(img_counter, timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # # # # #
    # FEATURE EXTRACTION  #
    # # # # # # # # # # # #
    log.heading("FEATURE EXTRACTION")
    if not SKIP_FIND_FEATURES:
        timer = Timer()

        if os.path.exists("{}/database.db".format(WORK_DIR)):
            os.remove("{}/database.db".format(WORK_DIR))

        # frame_dims = extractor.getDims()
        frame_dims = [FRAME_WIDTH, FRAME_HEIGHT]
        camera_model = settings["CAMERA_MODEL"]
        # camera_intrinsics = [settings["CAMERA_FOCAL_LENGTH"]] + [frame_dims[0]/2, frame_dims[1]/2] + settings["CAMERA_PARAMS"]
        camera_intrinsics = [settings["CAMERA_FOCAL_LENGTH"]] + [frame_dims[0]/2, frame_dims[1]/2]
        if settings["CAMERA_PARAMS"]:
            camera_intrinsics.append(settings["CAMERA_PARAMS"])

        camera_intrinsics_str = ",".join([str(d) for d in camera_intrinsics])

        raw_input = "{}/shell/feature_extract.sh {} {} {}".format(SCRIPT_DIR, WORK_DIR, camera_model, camera_intrinsics_str)
        args = shlex.split(raw_input)
        p = subprocess.Popen(args)
        p.wait()

        log.log("Feature extraction ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # # #
    # IMAGE MATCHING  #
    # # # # # # # # # #
    log.heading("IMAGE MATCHING")
    if not SKIP_FIND_MATCHES:
        timer = Timer()

        # FEATURE MATCHING
        VOCAB_TREE = "{}/vocab_tree/vocab_tree.bin".format(SCRIPT_DIR)
        raw_input = "{}/shell/match_vocabtree.sh {} {}".format(SCRIPT_DIR, WORK_DIR, VOCAB_TREE)
        args = shlex.split(raw_input)
        p = subprocess.Popen(args)
        p.wait()

        log.log("Image matching finished ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # # # # # #
    # SPARSE RECONSTRUCTION #
    # # # # # # # # # # # # #
    log.heading("MODEL RECONSTRUCTION")
    if not SKIP_RECONSTRUCT:
        timer = Timer()

        if not os.path.exists("{}/sparse".format(WORK_DIR)):
            os.mkdir("{}/sparse".format(WORK_DIR))

        target_num = settings["FRAMES_PER_MODEL"]
        overlap = settings["MODEL_OVERLAP"]
        num_chunks = int(round(float((NUM_FRAMES-overlap))/(target_num-overlap)))
        remainder = NUM_FRAMES - (target_num*num_chunks - overlap*num_chunks + overlap)

        log.log("Number of frames in model: {}".format(NUM_FRAMES))
        log.log("Target model size: {}".format(target_num))
        log.log("Model overlap: {}".format(overlap))
        log.log("Models to generate: {}".format(num_chunks))

        models = range(num_chunks)
        # OVERRIDE TO REGENERATE SPECIFIC MODELS
        # models = [0]

        for i in models:

            start_frame = i * (target_num - overlap)
            end_frame = start_frame + target_num

            if i == num_chunks-1:
                end_frame += remainder

            # MAKE IMAGE FILE
            print("\n\nCONSTRUCTING IMAGE LIST\n\n")
            make_image_list(start_frame, end_frame, WORK_DIR, VIDEO_PREFIX)

            MODEL_DIR = "{}/{}/{}".format(WORK_DIR, "sparse", i)
            if not os.path.exists(MODEL_DIR):
                os.mkdir(MODEL_DIR)

            timer_model = Timer()

            # RECONSTRUCT SPARSE
            raw_input = "{}/shell/sparse_reconstruct.sh {} {}".format(SCRIPT_DIR, WORK_DIR, i, 360, 361)
            args = shlex.split(raw_input)
            print args
            p = subprocess.Popen(args)
            p.wait()

            log.log("Constructed model [{}-{}]({} images) in directory: {} ({} sec)".format(start_frame, end_frame, end_frame-start_frame, MODEL_DIR, timer_model.read()))

        log.log("Reconstruction finished ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # #
    # MODEL MERGING #
    # # # # # # # # #
    log.heading("MODEL MERGING")
    if not SKIP_MERGE:
        timer = Timer()

        # FIND RECONSTRUCTED MODELS
        dirs = os.walk("{}/sparse".format(WORK_DIR))
        model_dirs = next(dirs)[1]
        models = []
        for model_dir in model_dirs:
            # try:
            models.append(int(model_dir))
        models.sort()

        log.log("Found {} models: {}".format(len(models), models))

        if len(models) > 1:

            if not os.path.exists("{}/merged".format(WORK_DIR)):
                os.mkdir("{}/merged".format(WORK_DIR))

            model_1 = "{}/sparse/{}/0".format(WORK_DIR,models.pop(0))

            for i,m in enumerate(models):

                model_2 = "{}/sparse/{}/0".format(WORK_DIR,m)
                merge_dir = "{}/merged/{}".format(WORK_DIR,i)
                if not os.path.exists(merge_dir):
                    os.mkdir(merge_dir)

                # MERGE MODEL
                raw_input = "{}/shell/model_merge.sh {} {} {}".format(SCRIPT_DIR, model_1, model_2, merge_dir)
                args = shlex.split(raw_input)
                print args
                p = subprocess.Popen(args)
                p.wait()

                # BUNDLE ADJUSTMENT
                # raw_input = "{}/shell/bundle_adjuster.sh {}".format(SCRIPT_DIR, merge_dir)
                # args = shlex.split(raw_input)
                # print args
                # p = subprocess.Popen(args)
                # p.wait()

                model_1 = merge_dir

                log.log("Merged models:\n{}\n{}\ninto model:\n{}".format(model_1, model_2, merge_dir))
        else:
            log.log("{} model(s) found, at least 2 needed for merging.".format(len(models)))

        log.log("Merging finished ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # # #
    # MODEL ALIGNMENT #
    # # # # # # # # # #
    log.heading("MODEL ALIGNMENT TO WORLD COORDINATES")
    if not SKIP_ALIGNMENT:
        timer = Timer()
        # FIND MODELS
        models = []
        merge_dir = "{}/merged/0".format(WORK_DIR)
        merge_flag = False

        if os.path.exists(merge_dir):
            models.append(merge_dir)
            merge_flag = True
        else:
            log.log("No merged model found at\n{}".format(merge_dir))
            dirs = os.walk("{}/sparse".format(WORK_DIR))
            model_dirs = next(dirs)[1]
            models = []
            for model_dir in model_dirs:
                # try:
                models.append(int(model_dir))
            models.sort()
            models = ["{}/sparse/{}/0/".format(WORK_DIR,m) for m in models]

        log.log("Found {} models:{}".format(len(models), '\n'.join(models)))

        images_dir = "{}/images".format(WORK_DIR)
        align_dir = "{}/sparse_aligned".format(WORK_DIR)
        if not os.path.exists(align_dir):
            os.mkdir(align_dir)

        for i,model in enumerate(models):
            # MERGE MODEL
            out_model = "{}/{}".format(align_dir,i)

            raw_input = "{}/shell/model_align.sh {} {} {}".format(SCRIPT_DIR, images_dir, model, out_model)
            args = shlex.split(raw_input)
            print args
            p = subprocess.Popen(args)
            p.wait()

            log.log("Aligned model:\n{}\ninto model:\n{}".format(model, out_model))

        log.log("Alignment finished ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    # # # # # # # # # # # # # #
    # SPARSE MODEL CONVERSION #
    # # # # # # # # # # # # # #
    log.heading("MODEL CONVERSION TO PLY")
    if not SKIP_SPARSE_CONVERT:
        timer = Timer()

        # FIND ALIGNED MODELS
        models = []
        align_dir = "{}/sparse_aligned/0".format(WORK_DIR)
        align_flag = False
        if os.path.exists(align_dir):
            models.append(align_dir)
            align_flag = True
        else:
            log.log("No aligned model found at\n{}".format(merge_dir))
            dirs = os.walk("{}/sparse".format(WORK_DIR))
            model_dirs = next(dirs)[1]
            models = []
            for model_dir in model_dirs:
                # try:
                models.append(int(model_dir))
            models.sort()
            models = ["{}/sparse/{}/0/".format(WORK_DIR,m) for m in models]

        log.log("Found {} models:{}".format(len(models), '\n'.join(models)))

        convert_dir = "{}/sparse_ply".format(WORK_DIR)
        if not os.path.exists(convert_dir):
            os.mkdir(convert_dir)

        for i,model in enumerate(models):
            # MERGE MODEL
            out_model = "{}/sparse_{}.ply".format(convert_dir,i) \
                if not align_flag else \
                "{}/sparse_aligned.ply".format(convert_dir)


            raw_input = "{}/shell/model_convert.sh {} {} {}".format(SCRIPT_DIR, model, out_model, "PLY")
            args = shlex.split(raw_input)
            print args
            p = subprocess.Popen(args)
            p.wait()

            log.log("Converted model:\n{}\ninto model:\n{}".format(model, out_model))

            input_bin = "{}/images.bin".format(model)
            CameraTrackExtractor.extract(input_bin, convert_dir)

            log.log("Created camera tracks in: {}".format(convert_dir))

        log.log("Conversion finished ({} sec)".format(timer.read()))
    else:
        log.log("Skipped")

    log.log("\n...job finished.")

if __name__ == "__main__":
    reconstruct(recon_settings)
