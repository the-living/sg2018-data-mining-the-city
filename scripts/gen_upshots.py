from helpers import VideoExtractor
import os, cv2

VIDEO_PATH = "/home/tl-admin/Dropbox/sg2018-data-mining-the-city/submission/fidi_01/FD-01.mp4"
OUT_DIR = "/home/tl-admin/Dropbox/sg2018-data-mining-the-city/submission/fidi_01/upshot"

def run(input_path, output_path):
    assert os.path.exists(input_path), "ERROR: Video file missing at {}".format(input_path)
    print("Generating UP frames from:\n{}".format(input_path))
    out_base = input_path.split("/")[-1].rstrip(".mp4")
    frame_grab = VideoExtractor(
        input_path,
        rescale=1,
        fov=2.0,
        pan=[0.5],
        tilt=[0.0]
        )

    for i in range(2):
        frame_name = "_U_{:05d}.jpg".format(i)
        print("\nGenerating: {}{}".format(out_base,frame_name))
        out_path = "{}/{}{}".format(output_path, out_base, frame_name)
        frame = frame_grab.extract(i)[0]
        cv2.imwrite(out_path, frame)

if __name__ == "__main__":
    run(VIDEO_PATH, OUT_DIR)
