from fiji.util.gui import GenericDialogPlus
from ij.io import OpenDialog
import os 
import glob
import re
from ij import IJ
from ij.plugin.frame import RoiManager
from ij.process import ImageStatistics
from ij.measure import Calibration, Measurements
from org.python.core import codecs
from ij.io import DirectoryChooser


DirectoryChooser("").setDefaultDirectory(OpenDialog.getDefaultDirectory())
codecs.setDefaultEncoding('utf-8')

def getImgRoiDir():    
     
    gui = GenericDialogPlus("Select directories to process images and ROI sets to apply")
     
    default_dir = OpenDialog.getDefaultDirectory()
    gui.addDirectoryField("Choose a iamge folder to be processed", default_dir)
    gui.addDirectoryField("Choose a ROI set folder to apply", default_dir)
    
    gui.showDialog()
    
    if gui.wasOKed():
       
        img_dir   = gui.getNextString()
        if not img_dir.endswith(os.sep):
            img_dir = img_dir + os.sep
            
        roi_dir = gui.getNextString()
        if not roi_dir.endswith(os.sep):
            roi_dir = roi_dir + os.sep
        
        return img_dir, roi_dir


img_dir, roi_dir = getImgRoiDir()  #


def get_file_list(parent_dir, identifier = ".tif"):

    if parent_dir is not None:
        file_list = glob.glob(parent_dir + "*" + identifier)
        return file_list
    else:
        pass


roiset_list = get_file_list(roi_dir, ".zip")
tif_list = get_file_list(img_dir, ".tif")


def get_img_names(tif_list):
    img_l = []
    for img_path in tif_list:
        img_file = os.path.basename(img_path)
        img_name = img_file.replace("-subtracted.tif", "")
        img_l.append(img_name)
    return img_l


def get_roi_names(roiset_list):
    roi_l = []
    for roi_path in roiset_list:
        roi_file = os.path.basename(roi_path)
        roi_name = re.sub(r"_RoiSet_\d*?.zip", "", roi_file)
        roi_l.append(roi_name)
    return roi_l


img_name_list = get_img_names(tif_list)
roi_name_list = get_roi_names(roiset_list)


def get_same_name(img_name_list, roi_name_list):
    
    same_name = []
    
    for img_name in img_name_list:
        if img_name in roi_name_list:
            same_name.append(img_name)
    
    return same_name


name_list = get_same_name(img_name_list, roi_name_list)


def measure_rm(img_path, roi_path):
    imp = IJ.openImage(img_path)
    img_dir = imp.getOriginalFileInfo().directory 
    img_file = imp.getOriginalFileInfo().fileName
    ip = imp.getProcessor()
    cal = Calibration(imp)
    
    rm = RoiManager()
    rm = RoiManager.getInstance()
    
    rm.runCommand("Open",roi_path)
    roi_array = rm.getRoisAsArray()
    
    moptions = Measurements.MEAN | Measurements.AREA
    
    for roi in roi_array:
        
        roi_name = roi.getName()
        ip.setRoi(roi)
        stat = ImageStatistics.getStatistics(ip, moptions, cal)
        # Measurementの値を指定するにはmoptionでMeasuremnt Classのbit論理和を取る
        
    
        IJ.log(
        img_dir + "\t" + 
        img_file + "\t" + 
        roi_name + "\t" + 
        str(stat.pixelCount) + "\t" + 
        str(stat.pixelCount*stat.umean) + "\t" + 
        str(stat.umean)
        )
    rm.runCommand("delete")

def measure_multi_roiset(name_list, tif_list, roiset_list):
    if name_list and tif_list and roiset_list is not None:
        for name in name_list:
            for tif in tif_list:
                for roiset in roiset_list:
                    if name in roiset and name in tif:
                        measure_rm(tif, roiset)
IJ.log("\\Clear") 

IJ.log(
       "Directory"+ "\t" +"File" + "\t" + 
       "Roi_id" + "\t" +  
       "Area" + "\t" + "Integrated_density" + "\t" + 
       "Mean_intensity"
)

measure_multi_roiset(name_list, tif_list, roiset_list)