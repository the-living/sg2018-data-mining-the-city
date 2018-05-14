import cv2
from colmap_database import COLMAPDatabase, blob_to_array
import numpy as np

DB_PATH = "vis/model/database.db"
IMG_PATH = "vis/model/images"
OUT_PATH = "vis/model/feature_labels_bw"

db = COLMAPDatabase.connect(DB_PATH)

rows = db.execute("SELECT * FROM keypoints")

for kp in rows:
    # kp = next(rows)
    img_name = db.execute("SELECT name FROM images WHERE image_id = {}".format(kp[0]))
    image_fp = next(img_name)[0]
    img = cv2.imread("{}/{}".format(IMG_PATH,image_fp),0)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    # print kp
    points = blob_to_array(kp[-1], np.float32,(kp[1],kp[2]))
    for pt in points:
        cv2.circle(
            img,
            tuple(pt[:2]),
            3,
            (0,0,255),
            thickness=-1)

    # cv2.imshow("frame", img)
    cv2.imwrite("{}/{}.label.jpg".format(OUT_PATH, image_fp.rstrip(".jpg")),img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

rows = db.execute("SELECT * FROM keypoints")



# for item in rows:
#     blob = item[-1]
#     print blob
#     # for subitem in item:
#     #     print subitem
