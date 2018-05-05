import os
import subprocess
import json
import shlex
from fitparse import FitFile

# SET TO True IF FFMPEG AVAILABLE FROM SYSTEM PATH
FFMPEG_SYS = True
# OTHERWISE SET TO FFMPEG EXECUTABLE
FFMPEG_PATH = ""

# /PATH/TO/VIDEO.MP4
VIDEO_PATH = "/Users/james/Dropbox/TL_WORKING/SmartGeometry/TEST_WORKFLOW/V0180034.MP4"
# START TIME (SEC)
VIDEO_START = 2
# END TIME (SEC)
VIDEO_END = 12

# /PATH/TO/FITFILE.FIT
FIT_PATH = "/Users/james/Dropbox/TL_WORKING/SmartGeometry/TEST_WORKFLOW/2018-03-28-17-55-09.fit"

def split_video(video_path, start, end):
    outpath = "{}.{:d}.{:d}.mp4".format(video_path, start, end)
    if os.path.exists(outpath):
        os.remove(outpath)
    inpath = video_path
    ff = "ffmpeg" if FFMPEG_SYS else FFMPEG_PATH
    start_min, start_sec = divmod(start, 60)
    end_min, end_sec = divmod(end, 60)
    # end_min -= start_min
    # end_sec -= start_sec
    # print "start: {:02d}:{:02d} end: {:02d}:{:02d}".format(start_min,start_sec,end_min,end_sec)
    raw_input = "{} -i {} -ss 00:{:02d}:{:02d} -t 00:{:02d}:{:02d} -c copy {}".format(
        ff,
        inpath,
        start_min,
        start_sec,
        end_min-start_min,
        end_sec-start_sec,
        outpath)
    args = shlex.split(raw_input)
    print(args)
    p = subprocess.Popen(args)
    p.wait()
    return args[-1]


def extract_audio(video_path):
    ff = "ffmpeg" if FFMPEG_SYS else FFMPEG_PATH
    outpath = "{}.audio.aac".format(video_path)
    if os.path.exists(outpath):
        os.remove(outpath)
    raw_input = "{} -i {} -vn -acodec copy {}".format(ff, video_path, outpath)
    args = shlex.split(raw_input)
    print(args)
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
    outpath = "{}.trimmed-{}-{}.json".format(fit_path, start, end)
    fitdata = load_fit_data(fit_path)
    counter=0
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
    audio_trim = extract_audio(video_trim)
    fit_trim = extract_fit_data(fit_path, start, end)

    print("Trimmed to start: {:d} / end: {:d}".format(start, end))
    print("Trimmed video:\n{}".format(video_trim))
    print("Trimmed audio:\n{}".format(audio_trim))
    print("Trimmed FIT file:\n{}".format(fit_trim))

if __name__ == "__main__":
    split_all(VIDEO_PATH, FIT_PATH, VIDEO_START, VIDEO_END)
