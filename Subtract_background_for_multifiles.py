def get_tif_list():
    """
    Tiff file のリストを得る関数
    """    
    from glob import glob
    from ij.io import DirectoryChooser
    
    parent_dir = DirectoryChooser("Choose").getDirectory()

    if parent_dir:
        tif_list = glob(parent_dir + "*" + ".tif")
        return tif_list
    else:
        pass



def subtract_back(file):
    
    """
    ImageJのSubtract backgroundを実行し, 
    開いた画像のDirectory内にSubtracted_imagesを作成し,
    背景画像を減算した画像を保存する。
    """  
    import os
    from ij import IJ
    
    imp = IJ.openImage(file)
    
    img_dir = imp.getOriginalFileInfo().directory

    save_dir = os.path.join(img_dir, "Subtracted_images")


    if not os.path.exists(save_dir):  # もしsave_dirが存在しなければそのディレクトリを作成
        os.makedirs(save_dir)

    
    img_file = imp.getOriginalFileInfo().fileName
    file_name, ext = os.path.splitext(img_file)


    save_path = os.path.join(save_dir, file_name + "-subtracted.tif")
    
    IJ.run(imp, "Subtract Background...", "rolling=30") # Radius 30
    IJ.saveAsTiff(imp, save_path)
    imp.close()



def apply_list(func, file_list=get_tif_list()):

    """
    file_listの中のファイル(file)を引数に持つ関数で処理を行う
    """
    if file_list:
        for file in file_list:
            func(file)
    else:
        pass
        

apply_list(func = subtract_back)
    



