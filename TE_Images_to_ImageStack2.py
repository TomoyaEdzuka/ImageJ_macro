from ij import IJ
from ij.io import DirectoryChooser
import glob
from java.awt import Color
from ij.plugin import HyperStackConverter
from ij.process import LUT
from ij.gui import GenericDialog
import os
import sys
import re

"""
Convert annoying images from TE to 
hyperstack images with your favorite channel colors from a dialog
"""

parent_dir = DirectoryChooser("Choose a directory").getDirectory()  # 処理するディレクトリをダイアログを使って取得する

if parent_dir:
    file_path = glob.glob(parent_dir + "*.tif")
else:
    IJ.log("Dialog was canceled")
    sys.exit()


def getTeNchannel(imp):
    """"
    TE画像からProperty情報を抜き出し,
    チャネルの数を取得する関数
    """
    try:
        prop = imp.getProperties().getProperty('Info')
    
    except:
        IJ.log('The image files do not have a channel property')
        raise Exception('The image files do not have channel properties')

    match = re.compile(r'Repeat - Channel \((.+)\)')
    channel_info = match.findall(prop)
    print("Channel contents: {}".format(channel_info))

    if channel_info:
        comma = channel_info[0].count(",")  # ","の出現回数からチャネルの数を計算する
        nChannel = comma + 1
        return nChannel
    else:
        IJ.log('The image files do not have a channel property')
        return


if file_path:
    imp0 = IJ.openImage(file_path[0])
    
    try:
        n_Channel = getTeNchannel(imp0)
    except:
        IJ.log('The image files do not have a channel property')
        raise Exception('The image files do not have a channel property')
    
    del imp0
else:
    IJ.log("No images found")
    sys.exit()



def get_color(nChannel = n_Channel):
    color_strings = ["Green", "Magenta", "Cyan",
                     "Blue", "Red", "Yellow",
                     "Orange", "Gray", "Black"]

    gd = GenericDialog("Set Colors")

    for i in range(nChannel):
        gd.addChoice("Channel {}".format(i + 1), color_strings, color_strings[i])

    gd.showDialog()

    if gd.wasCanceled():
        return
    else:
        selected_colours = [gd.getNextChoice() for _ in range(nChannel)]
        return selected_colours


user_color = get_color(nChannel=n_Channel)  # return a list of strings

if not user_color:
    IJ.log('The dialog was canceled')
    sys.exit()

Colors = {"Green": Color.green, "Magenta": Color.magenta,
          "Cyan": Color.cyan, "Blue": Color.blue, "Red": Color.red,
          "Yellow": Color.yellow, "Black": Color.black,
          "Orange": Color.orange, "Gray": Color.gray}

# Saveする Directoryの文字列を作成
dir_names = [s for s in parent_dir.split("/") if not s == '']
dir_depth = len(dir_names)
base_dir_name = dir_names[dir_depth - 1]
new_dir = "{}_HyperStacks".format(base_dir_name)

save_dir = os.path.join(parent_dir, new_dir)


# Saveするためのディレクトリと Alert Dialogを作成
def canceled():
    gd = GenericDialog("Caution")
    gd.addMessage('Tiff file(s) already exists in {}.\n \
    The file may be replaced by this macro run. Do you wish to continue?'.format(save_dir))
    gd.showDialog()
    return gd.wasCanceled()


if not os.path.exists(save_dir):  # もしsave_dirが存在しなければそのディレクトリを作成
    os.makedirs(save_dir)

if glob.glob(os.path.join(save_dir, "*.tif")):
    Canceled = canceled()
else:
    Canceled = False
    

if not Canceled:

    for f in file_path:
        
        # Hyperstackの作成
        imp = IJ.openImage(f)
        nFrame = imp.getNSlices() / n_Channel  # 元画像のAttributionがなぜかFrame が Z sliceとなっている
        
        # File 保存のための文字列作成
        save_file = imp.getTitle().replace(".tif", "-stack.tif")
        save_path = os.path.join(save_dir, save_file)

        # Hyper Stackに変換
        h_imp = HyperStackConverter.toHyperStack(imp, n_Channel, 1, nFrame, "Composite")

        del imp
        
        # Hyper Stack の Channelカラー変更
        for i, color in enumerate(user_color):
            h_imp.setC(i + 1)
            h_imp.setLut(LUT.createLutFromColor(Colors[color]))

        # ファイルを保存
        IJ.saveAsTiff(h_imp, save_path)
        # IJ.log(save_path)
        del h_imp


