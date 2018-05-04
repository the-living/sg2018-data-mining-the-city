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
from read_model import read_images_binary

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

class PerspectiveExtractor:
    # Extracts perspective projections from equirectangular inputs
    # Based on a modified version of "equirectangular-toolbox"
    # by Nitish Mutha https://github.com/NitishMutha/equirectangular-toolbox/
    def __init__(self, height=400, width=800, fov=0.45):
        self.FOV = [fov, fov]
        self.PI = math.pi
        self.PI_2 = math.pi * 0.5
        self.PI2 = math.pi * 2.0
        self.height = height
        self.width = width
        self.screen_points = self._get_screen_img()

    def _get_coord_rad(self, isCenterPt, center_point=None):
        return (center_point * 2 - 1) * np.array([self.PI, self.PI_2]) \
            if isCenterPt \
            else \
            (self.screen_points * 2 - 1) * np.array([self.PI, self.PI_2]) * (
                np.ones(self.screen_points.shape) * self.FOV)

    def _get_screen_img(self):
        xx, yy = np.meshgrid(np.linspace(0, 1, self.width), np.linspace(0, 1, self.height))
        return np.array([xx.ravel(), yy.ravel()]).T

    def _calcSphericaltoGnomonic(self, convertedScreenCoord):
        x = convertedScreenCoord.T[0]
        y = convertedScreenCoord.T[1]

        rou = np.sqrt(x ** 2 + y ** 2)
        c = np.arctan(rou)
        sin_c = np.sin(c)
        cos_c = np.cos(c)

        lat = np.arcsin(cos_c * np.sin(self.cp[1]) + (y * sin_c * np.cos(self.cp[1])) / rou)
        lon = self.cp[0] + np.arctan2(x * sin_c, rou * np.cos(self.cp[1]) * cos_c - y * np.sin(self.cp[1]) * sin_c)

        lat = (lat / self.PI_2 + 1.) * 0.5
        lon = (lon / self.PI + 1.) * 0.5

        return np.array([lon, lat]).T

    def _bilinear_interpolation(self, screen_coord):
        uf = np.mod(screen_coord.T[0],1) * self.frame_width  # long - width
        vf = np.mod(screen_coord.T[1],1) * self.frame_height  # lat - height

        x0 = np.floor(uf).astype(int)  # coord of pixel to bottom left
        y0 = np.floor(vf).astype(int)
        x2 = np.add(x0, np.ones(uf.shape).astype(int))  # coords of pixel to top right
        y2 = np.add(y0, np.ones(vf.shape).astype(int))

        base_y0 = np.multiply(y0, self.frame_width)
        base_y2 = np.multiply(y2, self.frame_width)

        A_idx = np.add(base_y0, x0)
        B_idx = np.add(base_y2, x0)
        C_idx = np.add(base_y0, x2)
        D_idx = np.add(base_y2, x2)

        flat_img = np.reshape(self.frame, [-1, self.frame_channel])

        A = np.take(flat_img, A_idx, axis=0)
        B = np.take(flat_img, B_idx, axis=0)
        C = np.take(flat_img, C_idx, axis=0)
        D = np.take(flat_img, D_idx, axis=0)

        wa = np.multiply(x2 - uf, y2 - vf)
        wb = np.multiply(x2 - uf, vf - y0)
        wc = np.multiply(uf - x0, y2 - vf)
        wd = np.multiply(uf - x0, vf - y0)

        # interpolate
        AA = np.multiply(A, np.array([wa, wa, wa]).T)
        BB = np.multiply(B, np.array([wb, wb, wb]).T)
        CC = np.multiply(C, np.array([wc, wc, wc]).T)
        DD = np.multiply(D, np.array([wd, wd, wd]).T)
        nfov = np.reshape(np.round(AA + BB + CC + DD).astype(np.uint8), [self.height, self.width, 3])
        # import matplotlib.pyplot as plt
        # plt.imshow(nfov)
        # plt.show()
        return nfov

    def toPerspective(self, frame, center_point):
        self.frame = frame
        self.frame_height = frame.shape[0]
        self.frame_width = frame.shape[1]
        self.frame_channel = frame.shape[2]

        self.cp = self._get_coord_rad(center_point=center_point, isCenterPt=True)
        convertedScreenCoord = self._get_coord_rad(isCenterPt=False)
        spericalCoord = self._calcSphericaltoGnomonic(convertedScreenCoord)
        return self._bilinear_interpolation(spericalCoord)


class VideoExtractor:
    def __init__(
        self,
        video_path,
        fit_path,
        rescale=None,
        frame_width=2160,
        frame_height=1080,
        fov=0.45,
        pan=[0.5, 0.75, 0.0, 0.25],
        tilt=[0.5]
        ):

        # LOAD VIDEOS
        # self.videos = []
        # for video_path in video_paths:
        #     self.videos.append(cv2.VideoCapture(video_path))
        #
        # template = self.videos[-1]
        self.video = cv2.VideoCapture(video_path)
        template = self.video

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

        self.pcam = PerspectiveExtractor(frame_height, frame_width, fov)
        self.pan = pan
        self.tilt = tilt

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

        # for video in self.videos:
        #     video.set(cv2.CAP_PROP_POS_MSEC, t_pos)

        self.video.set(cv2.CAP_PROP_POS_MSEC, t_pos)

        frames = []

        # for video in self.videos:
        #     ret, frame = video.read()
        #     frames.append(frame)

        ret, frame = self.video.read()
        for tilt in self.tilt:
            for pan in self.pan:
                center = np.array([pan, tilt])
                img = self.pcam.toPerspective(frame, center)
                frames.append(img)

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

class CameraTrackExtractor:
    def __init__(self, path_to_model_binary,dir_flag="N"):
        self.tracks = self._create_tracks(path_to_model_binary,dir_flag)

    def _q_mult(self, q1, q2):
        a1, b1, c1, d1 = q1
        a2, b2, c2, d2 = q2
        a = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
        b = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
        c = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
        d = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2
        return (a, b, c, d)

    def _rot_with_q(self, q, x):
        q_x = (0.0, x[0], x[1], x[2])
        q_inv = (q[0], -q[1], -q[2], -q[3])
        q_x_rot = self._q_mult(self._q_mult(q, q_x), q_inv)
        x_rot = q_x_rot[1:]
        return x_rot

    def _compute_wpos(self, q, xi, t):
        x_t_inv = (xi[0] - t[0], xi[1] - t[1], xi[2] - t[2])
        q_inv = (q[0], -q[1], -q[2], -q[3])
        pcenter_wpos = self._rot_with_q(q_inv, x_t_inv)
        return pcenter_wpos

    def _extract_xform(obj):
        pos_init = (0.0, 0.0, 0.0)
        target_init = (0.0, 0.0, 1.0)
        pos_new = self._compute_wpos(obj.qvec, pos_init, obj.tvec)
        target_new = self._compute_wpos(obj.qvec, target_init, obj.tvec)
        target_vec = [t-p for t,p in zip(target_new, pos_new)]
        return pos_new, target_vec

    def _create_tracks(self,model_binary, dir_flag="N"):
        tracks = []
        model_images = read_images_binary(model_binary)
        for i in model_images:
            image_name = model_images[i].name.rstrip(".jpg")
            if not image_name.split("_")[-2] == dir_flag:
                continue
            pos, target = extract_xform(model_images[i])
            tracks.append({"name":image_name, "pos":pos, "target":target})

        return tracks

    def export(self, out_path, save_JSON=True, save_CSV=True):

        if not os.path.exists(out_path):
            os.mkdir(out_path)

        if save_JSON:
            out_file = "{}/camera_tracks.json".format(out_path)
            json.dump(self.tracks, open(out_file,'w'), separators=(',',':'))

        if save_CSV:
            out_file = "{}/camera_tracks.csv".format(out_path)
            header = "name, pos_x, pos_y, pos_z, target_x, target_y, target_z\n"
            with open(out_file,'w') as f:
                f.write(header)
                for track in self.tracks:
                    track_pos = ",".join(map(str, track["pos"]))
                    track_target = ",".join(map(str, track["target"]))
                    line = "{},{},{}\n".format(track["name"],track_pos,track_target)
                    f.write(line)
            f.close()


def make_image_list(start_frame, end_frame, working_dir, prefix):

    if os.path.exists("{}/image_list.txt".format(working_dir)):
        os.remove("{}/image_list.txt".format(working_dir))

    image_list = []

    for i in range(start_frame, end_frame):
        for d in ['N','S','E','W']:
            image_list.append("{}_{}_{}.jpg".format(prefix, d, str(i).zfill(5)))

    with open("{}/image_list.txt".format(working_dir), 'wb') as f:
        f.write('\n'.join(image_list))
