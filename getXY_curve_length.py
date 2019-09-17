from ij import IJ
from ij.gui import Roi
from ij.plugin.frame import RoiManager
import csv
import glob
from ij.io import Opener
import math
import os
import re

imp = IJ.getImage()

def get_distance(x1, y1, x2, y2):
    d = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return d


def get_roi_length(roi):
    floatpolygon = roi.getFloatPolygon()
    length = 0
    xp = floatpolygon.xpoints
    yp = floatpolygon.ypoints
    for xs, ys, xe, ye in zip(xp[1:], yp[1:], xp[:len(xp) - 1], yp[:len(yp) - 1]):
        length += get_distance(xs, ys, xe, ye)
    return length


def fit_spline(roi):
    roi.fitSpline()


def get_xpoints(roi):
    floatpolygon = roi.getFloatPolygon()
    xp = floatpolygon.xpoints
    return xp


def get_ypoints(roi):
    floatpolygon = roi.getFloatPolygon()
    yp = floatpolygon.ypoints
    return yp


def get_start_x(roi):
    x_start = get_xpoints(roi)[0]
    return x_start


def get_start_y(roi):
    y_start = get_ypoints(roi)[0]
    return y_start


def get_end_x(roi):
    x_arr = get_xpoints(roi)
    x_end = x_arr[len(x_arr) - 1]
    return x_end


def get_end_y(roi):
    y_arr = get_ypoints(roi)
    y_end = y_arr[len(y_arr) - 1]
    return y_end


def get_straight_lengh(roi):
    floatpolygon = roi.getFloatPolygon()
    xp = floatpolygon.xpoints
    yp = floatpolygon.ypoints
    return get_distance(xp[0], yp[0], xp[len(xp) - 1], yp[len(yp) - 1])


def apply_roi_arr(func):
    rm = RoiManager()
    rm = rm.getInstance()
    roi_arr = rm.getRoisAsArray()  # => list

    result_list = []
    for roi in roi_arr:
        result = func(roi)
        if result is not None:
            result_list.append(result)

    return result_list


def rm_ext(file_name):
    while True:
        file_name, ext = os.path.splitext(file_name)
        if ext == '':
            break
    return file_name


def get_file_info(imp=IJ.getImage()):
    img_dir = imp.getOriginalFileInfo().directory
    img_file = imp.getOriginalFileInfo().fileName
    name = rm_ext(img_file)

    return img_dir, name


def make_roi_dir(img_dir, name):
    roi_dir = os.path.join(img_dir, "{}_RoiSets".format(name))
    if not os.path.exists(roi_dir):
        os.makedirs(roi_dir)
        return roi_dir
    else:
        return roi_dir


def get_max_from_string(file_list, pattern=r"_\d+.zip"):
    l = []
    for path in file_list:
        # print(path)
        match = re.search(pattern, path)
        if match:
            string = match.group()
            result_string = ""
            for s in string:
                if s.isdigit():
                    result_string += s
            result_int = int(result_string)
            l.append(result_int)
    return max(l)

def make_roi_path(roi_dir, name):
    roi_sets = glob.glob(roi_dir + os.sep + name + "*" + ".zip")
    if roi_sets != []:
        max_index = get_max_from_string(roi_sets)
        roi_path = os.path.join(roi_dir, "{0}_RoiSet_{1}.zip".format(name, max_index + 1))
    else:
        roi_path = os.path.join(roi_dir, "{0}_RoiSet_{1}.zip".format(name, 1))
    return roi_path


def save_roi_set(imp=IJ.getImage()):
    img_dir, name = get_file_info()
    roi_dir = make_roi_dir(img_dir, name)
    roi_path = make_roi_path(roi_dir, name)
    rm = RoiManager().getInstance()
    rm.deselect()
    rm.runCommand("Save", roi_path)
    rm.runCommand("delete")


apply_roi_arr(fit_spline)  # SplineFit を適用する
xps = apply_roi_arr(get_xpoints)
yps = apply_roi_arr(get_ypoints)
curve_lengths = apply_roi_arr(get_roi_length)
straight_lengths = apply_roi_arr(get_straight_lengh)
x_starts = apply_roi_arr(get_start_x)
y_starts = apply_roi_arr(get_start_y)
x_ends = apply_roi_arr(get_end_x)
y_ends = apply_roi_arr(get_end_y)
roi_index = [i + 1 for i in range(len(x_starts))]


dir_name = imp.getOriginalFileInfo().directory
file_name = imp.getOriginalFileInfo().fileName


# Preapre to write csv file
col_name = ["folder", "file",  "roi_index", "x", "y", "x_start", "y_start", "x_end", "y_end",  "curve_length",
            "straight_length"]

csv_path = os.path.join(get_file_info()[0], get_file_info()[1] + "_analyze.csv")

# New csv file is generated if the macro run on your image is the first time.
with open(csv_path, "a") as f1:
    with open(csv_path, "r") as f2:
        s = f2.read()
    if s == "":
        with open(csv_path, "w") as f3:
            writer = csv.writer(f3)
            writer.writerow(col_name)

# 上書きモードで値を書き込む
with open(csv_path, "a") as f:
    writer = csv.writer(f)
    for i in range(len(xps)):
        for j in range(len(xps[i])):
            writer.writerow([dir_name, file_name, roi_index[i], xps[i][j], yps[i][j], x_starts[i], y_starts[i], x_ends[i],
                            y_ends[i], curve_lengths[i], straight_lengths[i]])

save_roi_set(imp=IJ.getImage())

# table上に表示する
op = Opener()
op.openTable(csv_path)