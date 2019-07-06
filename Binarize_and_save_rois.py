from ij import IJ, Prefs
from ij.plugin.frame import RoiManager
from ij.io import DirectoryChooser
from ij.plugin.filter import BackgroundSubtracter
import os
import glob
import re


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


def getNextIndex(l, pattern = '._RoiSet_(\d).zip'):

    result_list = [re.findall(pattern, string) for string in l]
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
        roi_path = os.path.join(roi_dir, "{0}_RoiSet_{1}.zip".format(name, num))
    return roi_path




def binarize(f):

    Prefs.blackBackground = True
    imp = IJ.openImage(f)
    
    if imp:
        binimp = imp.duplicate()
        bs = BackgroundSubtracter()
        ip = binimp.getProcessor()
        bs.rollingBallBackground(ip, 15, False, False, False, True, True)
        
        IJ.run(binimp, "Unsharp Mask...", "radius=2 mask=0.9")
        
        def smooth(n=1):
            for i in range(n):
                IJ.run(binimp, "Smooth", "")
        
        smooth(10)
        IJ.setAutoThreshold(binimp, "Moments dark")
        IJ.run(binimp, "Make Binary", "thresholded remaining")
        
        smooth(12)
        
        
        IJ.setAutoThreshold(binimp, "Moments white")
        IJ.run(binimp, "Make Binary", "thresholded remaining")
        
        IJ.run(binimp, "Erode", "")
        IJ.run(binimp, "Dilate", "")
        
        IJ.run(binimp, "Analyze Particles...", "size=250-Infinity circularity=0.2-1.00 exclude clear add")
        binimp.close()
        
    else:
        pass


def save_roi_set(f):
    
    img_dir, name = get_file_info(f)
    roi_dir = make_roi_dir(img_dir)
    roi_path = make_roi_path(roi_dir, name)

    
    rm = RoiManager().getInstance()

    rm.deselect()

    rm.runCommand("Save",roi_path)
    rm.runCommand("delete")   


def bin_save_rois(f):
    binarize(f)
    save_roi_set(f)


def get_tif_list(parent_dir = DirectoryChooser("Choose").getDirectory()):

    if parent_dir is not None:
        tif_list = glob.glob(parent_dir + "*" + ".tif")
        return tif_list
    else:
        pass


def apply_list(func, file_list):

    if file_list is not None:
        for file in file_list:
            func(file)
    else:
        pass


tiffs = get_tif_list()
apply_list(func = bin_save_rois, file_list=tiffs)
