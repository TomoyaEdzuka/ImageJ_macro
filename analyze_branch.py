from ij import IJ
from ij.plugin.frame import RoiManager
from ij.gui import Roi, PolygonRoi, Overlay
import math
import os
from ij.process import FloatPolygon
from java.awt import Color
from ij.measure import Calibration, Measurements
from ij.process import ImageStatistics
import datetime
import csv
import glob
from ij.io import Opener
from datetime import datetime
from datetime import timedelta, tzinfo

imp = IJ.getImage()


def get_distance(x1, y1, x2, y2):
    l = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return l

def get_roi_length(roi):
    floatpolygon = roi.getFloatPolygon()
    length = 0
    xp = floatpolygon.xpoints
    yp = floatpolygon.ypoints
    for xs, ys, xe, ye in zip(xp[1:], yp[1:], xp[:len(xp)-1], yp[:len(yp)-1]):
        length += get_distance(xs, ys, xe, ye)
    return length

class filament(RoiManager):

    def __init__(self):
        super(filament, self).__init__()
        self.RoiManager = self.getInstance()
        self.roi_array = self.RoiManager.getRoisAsArray()
        for roi in self.roi_array:
            roi.fitSpline()

    def get_xy(self, i):
        roi = self.roi_array[i]
        floatpolygon = roi.getFloatPolygon()
        # coords = sorted(set(coords),key=coords.index)

        x = floatpolygon.xpoints
        y = floatpolygon.ypoints

        return x, y

    def get_length(self, i):
        xp, yp = self.get_xy(i)
        length = 0
        for xs, ys, xe, ye in zip(xp[1:], yp[1:], xp[:len(xp)-1], yp[:len(yp)-1]):
            length += get_distance(xs, ys, xe, ye)
        return length
        # return self.roi_array[i].getFloatPolygon().getLength(True)
    
    def get_straight_length(self, i):
        xs, ys = self.get_xy(i)
        return get_distance(xs[0], ys[0], xs[len(xs)-1], ys[len(ys)-1])
        
    def get_coord_min_distance(self, i):
        stem_poly = self.roi_array[0].getFloatPolygon()
        sx = stem_poly.xpoints
        sy = stem_poly.ypoints

        if i == 0:
            temp_min, stem_index, branch_index = 0, 0, 0
            stemx = sx[0]
            stemy = sy[0]
            branchx = stemx
            branchy = stemy
            return temp_min, stemx, stemy, stem_index, branchx, branchy, branch_index

        branch_poly = self.roi_array[i].getFloatPolygon()
        bx = branch_poly.xpoints
        by = branch_poly.ypoints

    

        for index in range(len(sx)):
            for j in range(len(bx)):
                if index == 0 and j == 0:
                    temp_min = get_distance(bx[j], by[j], sx[index], sy[index])
                    continue
                if temp_min >= get_distance(bx[j], by[j], sx[index], sy[index]):
                    # print "temp_min = ", temp_min, "index, j =", index, j
                    temp_min = get_distance(bx[j], by[j], sx[index], sy[index])
                    stem_index = index
                    branch_index = j
                    stemx = sx[index]
                    stemy = sy[index]
                    branchx = bx[j]
                    branchy = by[j]

        
        return temp_min, stemx, stemy, stem_index, branchx, branchy, branch_index

                

    def prune_branch(self, i): # i >= 1

        if i == 0:
            return
        
        temp_min, stemx, stemy, stem_index, branchx, branchy, branch_index = self.get_coord_min_distance(i)        
        poly = self.roi_array[i].getFloatPolygon()
        poly_npoints = poly.npoints
        
        poly_index = branch_index    
        if poly_npoints/2 >= poly_index:
            # print 'if', i+1
            newx = poly.xpoints[poly_index:]
            newy = poly.ypoints[poly_index:]
            new_poly = FloatPolygon(newx, newy)
        else:
            # print 'else', i+1
            newx = reversed(poly.xpoints[:poly_index + 1])
            newy = reversed(poly.ypoints[:poly_index + 1])
            new_poly = FloatPolygon(newx, newy)
                

        
        new_roi = PolygonRoi(new_poly, Roi.POLYLINE)
        new_roi.fitSpline()       
        self.RoiManager.setRoi(new_roi, i)

    def get_distance_from_stem(self, i):

        if i == 0:
            return 0
        min_len, stemx, stemy, stem_index, _1, _2, _3  = self.get_coord_min_distance(i)
        stem_x_array = self.roi_array[0].getFloatPolygon().xpoints[:stem_index]
        stem_y_array = self.roi_array[0].getFloatPolygon().ypoints[:stem_index]
        new_poly = FloatPolygon(stem_x_array, stem_y_array)
        new_roi = PolygonRoi(new_poly, Roi.POLYLINE)
        new_roi.fitSpline()
        
        
        return get_roi_length(new_roi)
        
    def get_angle(self, i):
        _, _, _, stem_index, _, _, _ = self.get_coord_min_distance(i)
        
        stem_x = self.get_xy(0)[0]
        stem_y = self.get_xy(0)[1]
        branch_x = self.get_xy(i)[0]
        branch_y = self.get_xy(i)[1]

        between_x = stem_x[stem_index]
        between_y = stem_y[stem_index]

        start_stem_x = stem_x[stem_index - 10]
        start_stem_y = stem_y[stem_index - 10]

        end_branch_x = branch_x[10]
        end_branch_y = branch_y[10]

        xpoints = [start_stem_x, between_x, end_branch_x]
        ypoints = [start_stem_y, between_y, end_branch_y]
        new_poly_roi = PolygonRoi(xpoints,ypoints,3,Roi.ANGLE)
        
        return new_poly_roi.getAngle()
        
        
    def get_convexfull_area(self, i, imp=IJ.getImage()):
        convexfull = self.roi_array[i].getFloatConvexHull()
        convexfull_roi = PolygonRoi(convexfull, Roi.POLYGON)
        imp.setRoi(convexfull_roi)
        
        moptions = Measurements.MEAN|Measurements.INTEGRATED_DENSITY|Measurements.AREA 
        ip = imp.getProcessor()
        cal = Calibration(imp)
        stat = ImageStatistics.getStatistics(ip, moptions, cal)
        
        convexfull_are = stat.area 
        return convexfull_are
    
    def get_solidity(self, i = 0, width = 1):
        convexfull_are = self.get_convexfull_area(i)
        roi_length = self.get_length(i)
        roi_area = roi_length*width
        return roi_area/convexfull_are



def set_name(i):
    if i == 0:
        name = "Stem"
    else:
        name = "Branch"
    return name
    



### 以下ファイル処理 ###
def rm_ext(file_name):
    while True:
        file_name, ext = os.path.splitext(file_name)
        if ext == '':
            break
    return file_name

def get_file_info(imp = IJ.getImage()):
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
        

def make_roi_path(roi_dir, name):
    roi_sets = glob.glob(roi_dir + os.sep + name + "*" + ".zip")
    roi_path = os.path.join(roi_dir, "{0}_RoiSet_{1}.zip".format(name, len(roi_sets)+1))
    return roi_path


def save_roi_set(imp = IJ.getImage()):
    
    img_dir, name = get_file_info()
    roi_dir = make_roi_dir(img_dir, name)
    roi_path = make_roi_path(roi_dir, name)

    Roi.setColor(Color.blue)
    rm = RoiManager().getInstance()  
    rm.deselect()
    rm.runCommand("Save",roi_path)

    ol = imp.getOverlay()
    if ol is None:
        ol = Overlay()
    for roi in rm.getRoisAsArray():
        ol.add(roi)
        imp.setOverlay(ol)
    
    rm.runCommand("delete")
    ol.setStrokeColor(Color.blue)
    Roi.setColor(Color.yellow)   

####

### 以下データ出力

fil = filament()
for i in range(len(fil.roi_array)):
    fil.prune_branch(i)
fil = filament()

ite = range(len(fil.roi_array))

exec_time = datetime.now()

## 出力するもの一覧
file_info = os.path.join(*get_file_info())
file_path = [file_info for _ in ite]
exec_times = [exec_time for _ in ite]
roi_id = [i+1 for i in ite]
types = [set_name(i) for i in ite]

curve_length = [fil.get_length(i) for i in ite]
straight_length = [fil.get_straight_length(i) for i in ite]
distance_from_stem_apical = [fil.get_distance_from_stem(i) for i in ite]
angle = [fil.get_angle(i) for i in ite]
convexfull_area = [fil.get_convexfull_area(i) for i in ite]


# csv fileに書き込む準備
for_csv_row = zip(file_path, exec_times, roi_id, types, curve_length, straight_length, distance_from_stem_apical, angle, convexfull_area)
col_name = ["file_path", "exec_times", "roi_id", "types", "curve_length", "straight_length", "distance_from_stem_apical", "angle", "convexfull_area"]


csv_path = os.path.join(get_file_info()[0], get_file_info()[1] + "_analyze.csv")


# ファイルに内容がある場合は何もせず, 内容がないときだけカラムを書き込む
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
    writer.writerows(for_csv_row)

# saveしたあとにoverlayに書き込んで線を青色に変える。
save_roi_set(imp = IJ.getImage())

# table上に表示する
op = Opener()
op.openTable(csv_path)

