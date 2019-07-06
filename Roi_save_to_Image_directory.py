from ij import IJ
from ij.plugin.frame import RoiManager
import os
import glob

def get_file_info(f):
    img_dir = IJ.openImage(f).getOriginalFileInfo().directory
    img_file = IJ.openImage(f).getOriginalFileInfo().fileName
    name, ext = os.path.splitext(img_file)
    
    return img_dir, name

def make_roi_dir(img_dir):
    roi_dir = os.path.join(img_dir, "RoiSets")
    if not os.path.exists(roi_dir):
        os.makedirs(roi_dir)
        return roi_dir
    else:
        return roi_dir
        pass


def getNextIndex(l):
    import re
    result_list = [re.findall('._RoiSet_(\d).zip', s) for s in l]
    def flatten(nested):
        """2重リストを解消"""
        return [item for inner in nested for item in inner]
    result_l = flatten(result_list)
    return int(max(result_l)) + 1


        

def make_roi_path(roi_dir, name):
    roi_sets = glob.glob(roi_dir + os.sep + name + "*" + ".zip")
    
    if not roi_sets:
        roi_path = os.path.join(roi_dir, "{0}_RoiSet_1.zip".format(name)) 
    else:
        num = getNextIndex(roi_sets)
        roi_path = os.path.join(img_dir, "{0}_RoiSet_{1}.zip".format(name, num))
    return roi_path

f = '/Users/Edzuka/Desktop/190611_TE DAPIstaining/GGH#30 20x 3s_4.tif'
img_dir, name = get_file_info(f)
roi_dir = make_roi_dir(img_dir)
roi_path = make_roi_path(roi_dir, name)

print roi_path


rm = RoiManager().getInstance()
rm.deselect()

rm.runCommand("Save",roi_path)
rm.runCommand("delete")
