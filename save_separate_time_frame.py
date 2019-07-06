from ij import IJ
from ij.io import DirectoryChooser
import os
from ij.plugin import Duplicator
import glob

# Time FrameをSeparateして
# ファイル名 + ハイフン(_)のあとに1からスタートするindex番号をつけてtifで保存します


def get_file_info(f):
    img_dir = IJ.openImage(f).getOriginalFileInfo().directory
    img_file = IJ.openImage(f).getOriginalFileInfo().fileName
    file_name, ext = os.path.splitext(img_file)

    return img_dir, file_name


def get_presave_path(f, dir_name = "Separate"):
    img_dir, file_name = get_file_info(f)
    subdirname = os.path.basename(os.path.dirname(img_dir))
    save_dir = os.path.join(img_dir,  subdirname + "_" + dir_name)
    pre_save_path = os.path.join(save_dir, file_name)
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    return save_dir, pre_save_path




def get_tif_list(parent_dir = DirectoryChooser("Choose").getDirectory()):

    if parent_dir is not None:
        tif_list = glob.glob(parent_dir + "*" + ".tif")
        return tif_list
    else:
        pass



def save_separate_tif(f):
    if f is not None:
        
        save_dir, pre_save_path = get_presave_path(f, dir_name = "Separate")
    
        imp = IJ.openImage(f)
    
        for i in range(imp.getNFrames()):
            imp.setT(i + 1)
            new_imp = Duplicator().crop(imp)
            IJ.saveAsTiff(new_imp, pre_save_path + "_{}.tif".format(i+1))



def apply_list(func, file_list):

    if file_list is not None:
        for file in file_list:
            func(file)
    else:
        pass

tiffs = get_tif_list()
apply_list(func = save_separate_tif, file_list=tiffs)

    
