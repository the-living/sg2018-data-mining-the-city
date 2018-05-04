import pprint
# import rhinoscriptsyntax as rs
import json
import os

def q_mult(q1, q2):

    a1, b1, c1, d1 = q1
    a2, b2, c2, d2 = q2

    a = a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2
    b = a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2
    c = a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2
    d = a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2

    return (a, b, c, d)

#test test
def rot_with_q(q, x):

    q_x = (0.0, x[0], x[1], x[2])
    q_inv = (q[0], -q[1], -q[2], -q[3])

    q_x_rot = q_mult(q_mult(q, q_x), q_inv)
    x_rot = q_x_rot[1:]

    return x_rot


def compute_wpos(q, xi, t):

    x_t_inv = (xi[0] - t[0], xi[1] - t[1], xi[2] - t[2])
    q_inv = (q[0], -q[1], -q[2], -q[3])

    pcenter_wpos = rot_with_q(q_inv, x_t_inv)
    return pcenter_wpos


def extract_and_load_xforms(images_path):

    xforms = []

    with open(images_path, 'rt') as images_file:

        is_xform_line = True

        while True:

            line = images_file.readline()

            if not line:
                break

            if line.startswith('#'):
                continue

            if is_xform_line:

                parts = line.split()

                image_id = int(parts[0]),
                q = tuple(float(p) for p in parts[1:5])
                t = tuple(float(p) for p in parts[5:8])
                camera_id = int(parts[8])
                name = parts[9]

                pcenter_ipos = (0.0, 0.0, 0.0)
                pcenter_wpos = compute_wpos(q, pcenter_ipos, t)

                forward_ipos = (0.0, 0.0, 1.0)
                forward_wpos = compute_wpos(q, forward_ipos, t)

                forward_dir = tuple(
                    f - p for f, p in zip(forward_wpos, pcenter_wpos)
                )

                xform = {
                    'image_id': image_id,
                    'q': q,
                    't': t,
                    'camera_id': camera_id,
                    'name': name,
                    'pcenter_wpos': pcenter_wpos,
                    'forward_dir': forward_dir
                }
                xforms.append(xform)

            is_xform_line = not is_xform_line

    xforms.sort(key=lambda x: x['name'][5:] + x['name'][3])

    return xforms

def zUp_to_yUp(pt_to_transform):
	pX = pt_to_transform[2]
	pY = pt_to_transform[0]
	pZ = - pt_to_transform[1]
	return (pX,pY,pZ)


path_data = {}
#path_data["cam_id"] = {}
#path_data["cam_id"]["coords"] = pt_coord
#path_data["cam_id"]["or_vector"] = vec

y_up = True
csv_cam_coords_fn = "cam_coords.csv"
csv_cam_vecs_fn = "cam_vecs.csv"

if __name__ == '__main__':

    images_path = 'images.txt'

    xforms = extract_and_load_xforms(images_path)
    pprint.pprint(xforms)

    pcenter_points = []
    forward_lines = []
    

    for i, xform in enumerate(xforms):
        
        # create json file
        cam_id_key = xform["name"]
        path_data[cam_id_key] = {}
        path_data[cam_id_key]["coords"] = xform["pcenter_wpos"]
        path_data[cam_id_key]["or_vector"] = xform["forward_dir"]

        # Camera position in world coordinates.
        pcenter_wpos = xform['pcenter_wpos']
        print(pcenter_wpos[0])
        # Camera forward direction (unit vector) in world coordinates.
        forward_dir = xform['forward_dir'] 


        # # Draw camera position.
        # print(forward_dir)
        # print(pcenter_wpos[0])
        # print("@@@@@######<<<<<")
        # if y_up:
        #     pcenter_wpos = zUp_to_yUp(pcenter_wpos)
        # # rh_point = rs.AddPoint(pcenter_wpos)
        # # pcenter_points.append(rh_point)

        # # Draw camera direction.
        # if y_up:
        #    forward_dir = zUp_to_yUp(forward_dir)
        # dir_end_wpos = \
        #     tuple(c + f for c, f in zip(pcenter_wpos, forward_dir))
        
        # # rh_line = rs.AddLine(pcenter_wpos, dir_end_wpos)
        # # forward_lines.append(rh_line)

# json_fp = os.path.join(json_dir, "cam_path.json")
out_fn = "cam_path_data.json"
with open(out_fn, 'w') as outfile:
    json.dump(path_data, outfile)

# write csv files
# save out camera pos as csv
with open(csv_cam_coords_fn, 'w') as out_file:
    for i, xform in enumerate(xforms):
        if i%4==0:
            parsed_line = "{},{},{},{}".format(i, pcenter_wpos[0],pcenter_wpos[1],pcenter_wpos[2])
            out_file.write(parsed_line)
            out_file.write('\n')
            print("{} wrote line: {}".format(out_file, parsed_line))

# save out camera pos as csv
with open(csv_cam_vecs_fn, 'w') as out_file:
    for i, xform in enumerate(xforms):
        if i%4==0:
            parsed_line = "{},{},{},{}".format(i, forward_dir[0],forward_dir[1],forward_dir[2])
            out_file.write(parsed_line)
            out_file.write('\n')
            print("{} wrote line: {}".format(out_file, parsed_line))  