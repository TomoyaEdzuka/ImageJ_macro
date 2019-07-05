from ij import IJ
from ij.plugin.frame import RoiManager
from ij.process import ImageStatistics
from ij.measure import Calibration, Measurements



imp = IJ.getImage()

img_dir = imp.getOriginalFileInfo().directory 
img_file = imp.getOriginalFileInfo().fileName

if img_dir and img_file:
    pass

else:
    img_dir = "None"
    img_file = imp.getTitle()


ip = imp.getProcessor()
cal = Calibration(imp)

rm = RoiManager.getInstance()
roi_list = rm.getRoisAsArray()

# ビット論理和を取ることで設定したい値を変えられる
moptions =  Measurements.MEAN | Measurements.AREA


IJ.log("\\Clear") 

IJ.log(
       "Directory"+ "\t" +"File" + "\t" + 
       "Roi_id" + "\t" + "Object" + "\t" +  
       "Area" + "\t" + "Integrated_density" + "\t" + 
       "Mean_intensity"
)
  

for roi in roi_list:
    
    roi_name = roi.getName()
    roi_name_sp = roi_name.split("_")
    if len(roi_name_sp) >= 2:
        roi_id = roi_name_sp[0]
        obj = roi_name_sp[1]
    else:
        roi_id = roi_name_sp[0]
        obj = "None"
        
    
    ip.setRoi(roi)
    stat = ImageStatistics.getStatistics(ip, moptions, cal)
    # Measurementの値を指定するにはmoptionでMeasuremnt Classのbit論理和を取る
    

    IJ.log(
    img_dir + "\t" + 
    img_file + "\t" + 
    roi_id + "\t" + 
    obj + "\t" + 
    str(stat.pixelCount) + "\t" + 
    str(stat.pixelCount*stat.umean) + "\t" + 
    str(stat.umean)
    )
    
