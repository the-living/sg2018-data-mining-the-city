import cv2
from colmap_database import COLMAPDatabase, blob_to_array
import numpy as np

# POINT TO SPARSE RECONSTRUCTION DATABASE (.DB)
DB_PATH = "vis/model/database.db"
# POINT TO SPARSE RECONSTRUCTION IMAGES FOLDER
IMG_PATH = "vis/model/images"
# POINT TO OUTPUT PATH FOR SAVED IMAGES
OUT_PATH = "vis/model/feature_labels_bw"

db = COLMAPDatabase.connect(DB_PATH)

rows = db.execute("SELECT * FROM keypoints")

for kp in rows:
    img_name = db.execute("SELECT name FROM images WHERE image_id = {}".format(kp[0]))
    image_fp = next(img_name)[0]
    img = cv2.imread("{}/{}".format(IMG_PATH,image_fp),0)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    points = blob_to_array(kp[-1], np.float32,(kp[1],kp[2]))
    for pt in points:
        cv2.circle(
            img,
            tuple(pt[:2]),
            3,
            (0,0,255),
            thickness=-1)
    cv2.imwrite("{}/{}.label.jpg".format(OUT_PATH, image_fp.rstrip(".jpg")),img)

db.close()
