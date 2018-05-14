import os
import subprocess
import json
import shlex
from fitparse import FitFile

# IF FFMPEG AVAILABLE FROM SYSTEM PATH
FFMPEG_SYS = True
# OTHERWISE SET TO DOWNLOADED FFMPEG EXECUTABLE (ffmpeg.exe)
FFMPEG_PATH = ""

# OUTPUT DIRECTORY
OUT_DIR = "/path/to/output/folder"
OUT_NAME = "AB-01"

# /PATH/TO/VIDEO.MP4
VIDEO_PATH = "/path/to/source_video.mp4"
# START TIME (SEC)
VIDEO_START = 0
# END TIME (SEC)
VIDEO_END = 180

# /PATH/TO/FITFILE.FIT
FIT_PATH = "/path/to/fitfile.fit"

def split_video(video_path, start, end):
    ff = "ffmpeg" if FFMPEG_SYS else FFMPEG_PATH
    outpath = "{}/{}.mp4".format(OUT_DIR, OUT_NAME)

    if os.path.exists(outpath):
        os.remove(outpath)

    start_min, start_sec = divmod(start, 60)
    end_min, end_sec = divmod(end, 60)
    raw_input = "{} -i {} -ss 00:{:02d}:{:02d} -to 00:{:02d}:{:02d} -vcodec copy -an {}".format(
        ff,
        video_path,
        start_min,
        start_sec,
        end_min,
        end_sec,
        outpath)

    args = shlex.split(raw_input)
    # print(args)
    p = subprocess.Popen(args)
    p.wait()
    # RETURN PATH TO SAVED FILE
    return args[-1]


def extract_audio(video_path, start, end):
    ff = "ffmpeg" if FFMPEG_SYS else FFMPEG_PATH
    outpath = "{}/{}.aac".format(OUT_DIR, OUT_NAME)

    if os.path.exists(outpath):
        os.remove(outpath)

    start_min, start_sec = divmod(start, 60)
    end_min, end_sec = divmod(end, 60)
    raw_input = "{} -i {} -ss 00:{:02d}:{:02d} -to 00:{:02d}:{:02d} -vn -acodec copy {}".format(
        ff,
        video_path,
        start_min,
        start_sec,
        end_min,
        end_sec,
        outpath)

    args = shlex.split(raw_input)
    # print(args)
    p = subprocess.Popen(args)
    p.wait()
    return args[-1]

def load_fit_data(fp):
    data = FitFile(fp)
    values = {}

    for record in data.get_messages('record'):
        entry = {}
        timestamp = -1

        for record_data in record:
            if "timestamp" in record_data.name:
                timestamp = record_data.value
                continue

            entry[record_data.name] = [
                record_data.value,
                record_data.units if record_data.units else None]
        values[timestamp] = entry
    return values

def extract_fit_data(fit_path,start,end):
    records = {}

    outpath = "{}/{}_SENSOR_DATA.json".format(OUT_DIR, OUT_NAME)

    fitdata = load_fit_data(fit_path)
    counter = 0
    for t in xrange(start, end):
        timestamp = "{:05d}".format(t-start)
        if t in fitdata:
            records[timestamp] = fitdata[t]
            counter += 1

    print "Saving {:d} records to: {}".format(counter, outpath)

    with open(outpath, mode='w') as f:
        json.dump( records, f, sort_keys=True, indent=4, separators=(',',':'), default=str)
    f.close()

    return outpath

def split_all(video_path, fit_path, start, end):
    video_trim = split_video(video_path, start, end)
    audio_trim = extract_audio(video_trim, start, end)
    fit_trim = extract_fit_data(fit_path, start, end)

    print("Trimmed to start: {:d} / end: {:d}".format(start, end))
    print("Trimmed video:\n{}".format(video_trim))
    print("Trimmed audio:\n{}".format(audio_trim))
    print("Trimmed FIT file:\n{}".format(fit_trim))

if __name__ == "__main__":
    split_all(VIDEO_PATH, FIT_PATH, VIDEO_START, VIDEO_END)
