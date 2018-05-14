import cv2
from colmap_database import COLMAPDatabase, blob_to_array, pair_id_to_image_ids
import numpy as np

DB_PATH = "vis/model/database.db"
IMG_PATH = "vis/model/images"
OUT_PATH = "vis/model/image_match"

db = COLMAPDatabase.connect(DB_PATH)

rows = db.execute("SELECT * FROM images")

maxmatch = {}

for img in rows:
    if img[0] not in maxmatch:
        maxmatch[img[0]] = None

# db.execute("SELECT pair_id FROM inlier_matches WHERE ") image_id is

rows = db.execute("SELECT * FROM inlier_matches")

for match in rows:
    id1,id2 = pair_id_to_image_ids(match[0])
    if maxmatch[id1] is None:
        maxmatch[id1] = [match[0],match[1],1]
    elif maxmatch[id1][1] < match[1]:
        maxmatch[id1] = [match[0],match[1],1]

    if maxmatch[id2] is None:
        maxmatch[id2] = [match[0],match[1],2]
    elif maxmatch[id2][1] < match[1]:
        maxmatch[id2] = [match[0],match[1],2]

for img in maxmatch.keys():
    img1,img2 = pair_id_to_image_ids(maxmatch[img][0])
    img1_name = next(db.execute("SELECT name FROM images WHERE image_id = {}".format(img1)))[0]
    img2_name = next(db.execute("SELECT name FROM images WHERE image_id = {}".format(img2)))[0]

    pair_match_data = next(db.execute("SELECT data FROM inlier_matches WHERE pair_id = {}".format(maxmatch[img][0])))[0]
    pair_matches = blob_to_array(pair_match_data, np.uint32, (-1,2))

    img1_kp_data = next(db.execute("SELECT data FROM keypoints WHERE image_id = {}".format(img1)))[0]
    img1_kp = blob_to_array(img1_kp_data, np.float32, (-1,6))

    img2_kp_data = next(db.execute("SELECT data FROM keypoints WHERE image_id = {}".format(img2)))[0]
    img2_kp = blob_to_array(img2_kp_data, np.float32, (-1,6))

    img1_px = cv2.cvtColor(cv2.imread("{}/{}".format(IMG_PATH, img1_name), 0), cv2.COLOR_GRAY2BGR)
    img2_px = cv2.cvtColor(cv2.imread("{}/{}".format(IMG_PATH, img2_name), 0), cv2.COLOR_GRAY2BGR)

    h,w = img1_px.shape[:2]
    spacer = 20
    alpha = 0.2

    space_frame = np.zeros([h,spacer,3],dtype=np.uint8)

    out_img = np.hstack((img1_px, space_frame))
    out_img = np.hstack((out_img, img2_px))

    offset = np.array([w+spacer,0], dtype=np.float32)


    for kp in img1_kp:
        cv2.circle(
                    out_img,
                    tuple(kp[:2]),
                    3,
                    (255,0,0),
                    thickness=1)

    for kp in img1_kp:
        cv2.circle(
                    out_img,
                    tuple(np.add(kp[:2],offset)),
                    3,
                    (255,0,0),
                    thickness=1)

    base_img = out_img.copy()

    for a, b in pair_matches:

        # overlay = np.zeros(out_img.shape, dtype=np.uint8)

        pt1 = tuple(img1_kp[a][:2])
        pt2 = img2_kp[b][:2]

        pt2 = tuple(np.add(pt2,offset))

        # print pt1, pt2
        cv2.line(out_img, pt1, pt2, (0,0,255), 2)
        # cv2.line(overlay, pt1, pt2, (0,0,255), 2)

        # out_img = cv2.addWeighted(overlay, 0.25, out_img, 1, 1)
        # out_img = cv2.add(out_img, overlay)
    out_img = cv2.addWeighted(out_img, 0.5, base_img, 0.5, 1)


    outpath = "{}/{}".format(OUT_PATH, img1_name)
    print("SAVED: {}".format(img))
    cv2.imwrite(outpath, out_img)

db.close()



    # blob = blob_to_array(row[-1], np.uint32, (-1,2))
    # print blob
#
# for kp in rows:
#     # kp = next(rows)
#     img_name = db.execute("SELECT name FROM images WHERE image_id = {}".format(kp[0]))
#     image_fp = next(img_name)[0]
#     img = cv2.imread("{}/{}".format(IMG_PATH,image_fp),0)
#     img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#
#     # print kp
#     points = blob_to_array(kp[-1], np.float32,(kp[1],kp[2]))
#     for pt in points:
#         cv2.circle(
#             img,
#             tuple(pt[:2]),
#             3,
#             (0,0,255),
#             thickness=-1)
#
#     # cv2.imshow("frame", img)
#     cv2.imwrite("{}/{}.label.jpg".format(OUT_PATH, image_fp.rstrip(".jpg")),img)
#     # cv2.waitKey()
#     # cv2.destroyAllWindows()
#
# rows = db.execute("SELECT * FROM keypoints")



# for item in rows:
#     blob = item[-1]
#     print blob
#     # for subitem in item:
#     #     print subitem
