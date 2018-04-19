# OpenCV
import cv2
import numpy as np
# Supplemental Data
import piexif
from fitparse import FitFile
# General
import math
import json
import os
from glob import glob
import time

class LogWriter:

    def __init__(self, work_dir):
        self.id = time.strftime("%y%m%d_%H%M%S", time.localtime())
        self.file_name = "{}/{}".format(work_dir, "log_" + self.id + ".txt")
        with open(self.file_name, 'wb') as f:
            f.write("Starting job...")

    def heading(self, text):
        with open(self.file_name, 'ab') as f:
            f.write("\n\n"+text)
            f.write("\n========")

    def log(self, text):
        with open(self.file_name, 'ab') as f:
            f.write("\n" + text)


class Timer:

    def __init__(self):
        self.time = time.time()

    def read(self):
        return time.time() - self.time


class VideoExtractor:
    def __init__(self, video_paths, fit_path, rescale=None):

        # LOAD VIDEOS
        self.videos = []
        for video_path in video_paths:
            self.videos.append(cv2.VideoCapture(video_path))

        template = self.videos[-1]

        self.end = template.get(cv2.CAP_PROP_FRAME_COUNT) / float(template.get(cv2.CAP_PROP_FPS))
        self.width = template.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = template.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.rescale = rescale != 1
        if self.rescale:
            self.width = int(self.width * rescale)
            self.height = int(self.height * rescale)
            self.scale_method = cv2.INTER_AREA
            if rescale < 1:
                self.scale_method = cv2.INTER_LINEAR

        self.fitdata = self.loadFitData(fit_path)

        # if exif_path is not None:
        #     self.exif = piexif.load(exif_path)
        #     del self.exif["thumbnail"]
        #     self.exif["0th"][piexif.ImageIFD.ImageWidth] = (self.width,1)
        #     self.exif["0th"][piexif.ImageIFD.ImageLength] = (self.height,1)
        #     self.exif["1st"][piexif.ImageIFD.ImageWidth] = (self.width,1)
        #     self.exif["1st"][piexif.ImageIFD.ImageLength] = (self.height,1)
        # else:
        #     self.exif = None

    def getDims(self):
        return [self.width, self.height]

    def getEnd(self):
        return self.end

    def loadFitData(self, fp):
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

    def extract(self, time):

        if time > (self.end):
            return [None]

        t_pos = time * 1000

        for video in self.videos:
            video.set(cv2.CAP_PROP_POS_MSEC, t_pos)

        frames = []

        for video in self.videos:
            ret, frame = video.read()
            frames.append(frame)

        if self.rescale:
            frames = [cv2.resize(frame, (self.width,self.height), self.scale_method) for frame in frames]

        record = {}
        if time in self.fitdata:
            record = self.fitdata[time]
        else:
            print("No FIT record for T{}".format(time))
        return frames + [record]

    def semicircles2dd(self,sc):
        return sc * (180/float(2.0**31))

    def dd2dms(self, dd):
        mnt, sec = divmod(dd*3600, 60)
        deg, mnt = divmod(mnt, 60)
        return ((int(deg),1), (int(mnt),1), (int(sec*1000000),1000000))

    def writeEXIF(self, file_paths, values):
        newexif = self.exif.copy()
        # UPDATE EXIF DATA WITH GPS DATA
        if values:
            del newexif["GPS"]
            gps = {}
            if "position_lat" in values:
                latitude = self.semicircles2dd(int(values["position_lat"][0]))
                longitude = self.semicircles2dd(int(values["position_long"][0]))
                gps[piexif.GPSIFD.GPSLatitudeRef] = 'N' if latitude > 0 else 'S'
                gps[piexif.GPSIFD.GPSLongitudeRef] = 'E' if longitude > 0 else 'W'
                gps[piexif.GPSIFD.GPSLatitude] = self.dd2dms(abs(latitude))
                gps[piexif.GPSIFD.GPSLongitude] = self.dd2dms(abs(longitude))
            if "enhanced_altitude" in values:
                elev = values["enhanced_altitude"][0]
                gps[piexif.GPSIFD.GPSAltitudeRef] = 0 if elev >= 0 else 1
                gps[piexif.GPSIFD.GPSAltitude] = (abs(int(elev*1000000)),10000000)
            newexif["GPS"] = gps
        else:
            del newexif["GPS"]

        # STRIP ANY EXISTING EXIF DATA
        for file_path in file_paths:
            piexif.remove(file_path)

        # CONVERT EXIF DICT TO BYTES
        exif_bytes = piexif.dump(newexif)

        # INSERT EXIF DATA INTO IMAGE FILE
        for file_path in file_paths:
            piexif.insert(exif_bytes, file_path)


class SIFTExtractor:
    def __init__(self):
        self.sift = cv2.xfeatures2d.SIFT_create()

    def process(self, img, mask, label=False):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        kp, des = self.sift.detectAndCompute(gray, mask)
        return kp, des

    def label(self, img, kp, copy=True, gray=False):
        img_ = img
        if copy:
            img_ = img.copy()
        if gray:
            img_ = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
        return cv2.drawKeypoints(
            img_,
            kp,
            None,
            flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
        )

    def saveTXT(self, kp, des, fp):
        try:
            k, d = des.shape
            with open("{}.txt".format(fp), mode='w') as f:
                line = "{} {}\n".format(k, d)
                f.write(line)
                for i, ky in enumerate(kp):
                    k_pt = ky.pt
                    k_sz = ky.size
                    k_a = ky.angle
                    line = "{} {} {} {}".format(k_pt[0], k_pt[1], k_sz, k_a)
                    for d_ in xrange(d):
                        line += " {}".format(int(des[i][d_]))
                    line += "\n"
                    f.write(line)
            f.close()
            return True
        except:
            return False


def make_image_list(start_frame, end_frame, working_dir, prefix):

    if os.path.exists("{}/image_list.txt".format(working_dir)):
        os.remove("{}/image_list.txt".format(working_dir))

    image_list = []

    for i in range(start_frame, end_frame):
        for d in ['N','S','E','W']:
            image_list.append("{}_{}_{}.jpg".format(prefix, d, str(i).zfill(5)))

    with open("{}/image_list.txt".format(working_dir), 'wb') as f:
        f.write('\n'.join(image_list))
