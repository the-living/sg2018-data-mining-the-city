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


class VideoExtractor:
    def __init__(self, video_path_front, video_path_back, fit_path, exif_path, rescale=None):
        # LOAD VIDEOS
        self.video_a = cv2.VideoCapture(video_path_front)
        self.video_b = cv2.VideoCapture(video_path_back)

        #assert self.video_a.get(cv2.CAP_PROP_FRAME_COUNT) == self.video_b.get(cv2.CAP_PROP_FRAME_COUNT), "ERROR: FRONT/BACK VIDEOS HAVE MISMATCHED LENGTHS"

        self.end = self.video_a.get(cv2.CAP_PROP_FRAME_COUNT) / float(self.video_a.get(cv2.CAP_PROP_FPS))

        self.width = self.video_a.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.video_a.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.rescale = rescale != 1
        if self.rescale:
            self.width = int(self.width * rescale)
            self.height = int(self.height * rescale)
            self.scale_method = cv2.INTER_AREA
            if rescale < 1:
                self.scale_method = cv2.INTER_LINEAR

        self.fitdata = self.loadFitData(fit_path)

        self.exif = piexif.load(exif_path)
        del self.exif["thumbnail"]
        self.exif["0th"][piexif.ImageIFD.ImageWidth] = (self.width,1)
        self.exif["0th"][piexif.ImageIFD.ImageLength] = (self.height,1)
        self.exif["1st"][piexif.ImageIFD.ImageWidth] = (self.width,1)
        self.exif["1st"][piexif.ImageIFD.ImageLength] = (self.height,1)

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
            return None, None, None

        t_pos = time * 1000
        self.video_a.set(cv2.CAP_PROP_POS_MSEC, t_pos)
        self.video_b.set(cv2.CAP_PROP_POS_MSEC, t_pos)

        ret, frame_a = self.video_a.read()
        ret, frame_b = self.video_b.read()

        if self.rescale:
            frame_a = cv2.resize(frame_a, (self.width,self.height), self.scale_method)
            frame_b = cv2.resize(frame_b, (self.width,self.height), self.scale_method)

        record = {}
        if time in self.fitdata:
            record = self.fitdata[time]
        else:
            print("No FIT record for T{}".format(time))
        return frame_a, frame_b, record

    def semicircles2dd(self,sc):
        return sc * (180/float(2.0**31))

    def dd2dms(self, dd):
        mnt, sec = divmod(dd*3600, 60)
        deg, mnt = divmod(mnt, 60)
        return ((int(deg),1), (int(mnt),1), (int(sec*1000000),1000000))

    def writeEXIF(self, pathA, pathB, values):
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
        piexif.remove(pathA)
        piexif.remove(pathB)

        # CONVERT EXIF DICT TO BYTES
        exif_bytes = piexif.dump(newexif)

        # INSERT EXIF DATA INTO IMAGE FILE
        piexif.insert(exif_bytes, pathA)
        piexif.insert(exif_bytes, pathB)


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
