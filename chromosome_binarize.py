from ij import IJ, Prefs
from ij.plugin.frame import RoiManager
import os


# Binarize
imp = IJ.getImage()
imp1 = imp.duplicate()
IJ.run(imp1, "Subtract Background...", "rolling=15 stack")
IJ.run(imp1, "Median...", "radius=2 stack")
IJ.run(imp1, "Gaussian Blur...", "sigma=2 stack")
Prefs.blackBackground = True;
IJ.run(imp1, "Convert to Mask", "method=MaxEntropy background=Dark calculate black")
IJ.run(imp1, "Analyze Particles...", "size=400-Infinity pixel exclude add stack")
imp1.show()

# Analyze by using ROI manger
rm = RoiManager()
rm = RoiManager.getInstance()

roi_array = rm.getRoisAsArray()

# xyで構成される入れ子構造を組みかえる
def xypoint_flatten(roi_array = RoiManager.getInstance().getRoisAsArray()):
    if roi_array is not None:
        xpoint = [[] for _ in range(len(roi_array))]
        ypoint = [[] for _ in range(len(roi_array))]
        for i, roi in enumerate(roi_array):
            xy_coord = list(roi.getContainedPoints())
            for j, coord in enumerate(xy_coord):
                xpoint[i].append(coord.x)
                ypoint[i].append(coord.y)
    return xpoint, ypoint
    

xpoint,ypoint = xypoint_flatten()

def getRoiPosition(roi_array = RoiManager.getInstance().getRoisAsArray()):
    return [roi.getPosition() for roi in roi_array]


frame_position = getRoiPosition()
# print getRoiPosition()

def getRoiName(roi_array = RoiManager.getInstance().getRoisAsArray()):
    return [roi.getName() for roi in roi_array]

roi_name = getRoiName()

def flatten(nested):
    """2重リストを解消"""
    return [item for inner in nested for item in inner]


def getRoiCentroid(roi_array = RoiManager.getInstance().getRoisAsArray()):
    
    flat = flatten([roi.getContourCentroid() for roi in roi_array])
    xcentroid = flat[0::2] # index0からスタートして2つ刻み
    ycentroid = flat[1::2] # index1からスタートして2つ刻み
    return xcentroid, ycentroid
    # return flat

xcentroid, ycentroid = getRoiCentroid()

def getArea(roi_array = RoiManager.getInstance().getRoisAsArray()):
    return [roi.getStatistics().area for roi in roi_array]

area = getArea()

IJ.log("\\Clear")
IJ.log(
"Roi_id" + "\t" + 
"frame_position" + "\t" +
"area" + "\t" +
"xcentroid" + "\t" +
"ycentroid" + "\t" +
"xpoint" + "\t" +
"ypoint"
)


def write_log(roi_name, frame_position, area,  xcentroid, ycentroid, xpoint, ypoint):
    for i in range(len(roi_array)):
        IJ.log(
        roi_name[i] + "\t" + 
        str(frame_position[i]) + "\t" +
        str(area[i]) + "\t" +
        str(xcentroid[i]) + "\t" +
        str(ycentroid[i]) + "\t" +
        str(xpoint[i]) + "\t" +
        str(ypoint[i])
        ) 

write_log(roi_name, frame_position, area, xcentroid, ycentroid, xpoint, ypoint)




def get_file_info(imp):
    img_dir = imp.getOriginalFileInfo().directory
    img_file = imp.getOriginalFileInfo().fileName
    if img_dir and img_file is not None:
        name, ext = os.path.splitext(img_file)
        return img_dir, name


def make_roi_path(img_dir, name):
    if img_dir is not None:
        roi_path = os.path.join(img_dir, name + "_RoiSets.zip")
        return roi_path




### save Roi Set
def save_roi_set(imp):
    
    img_dir, name = get_file_info(imp)
    roi_path = make_roi_path(img_dir, name)
   
    rm = RoiManager().getInstance()

    rm.deselect()
    if roi_path is not None:
        rm.runCommand("Save",roi_path)
        rm.runCommand("delete")
save_roi_set(imp)

