import glob
import os
from ij.io import DirectoryChooser as dc
from loci.plugins. in import ImagePlusReader, ImporterOptions, ImportProcess
from org.python.core import codecs
from ij import IJ
from ij.gui import GenericDialog

codecs.setDefaultEncoding('utf-8')


def get_file_list():
    parent_dir = dc("Choose").getDirectory()

    if parent_dir is not None:
        file_list = glob.glob(parent_dir + "*")
        return file_list
    else:
        pass


def trans_to_tif(file_list, overwrite = False):
    if file_list is not None:
        for path in file_list:
            opts = ImporterOptions()
            opts.setId(path)
            opts.setVirtual(True)
            opts.setColorMode(ImporterOptions.COLOR_MODE_COMPOSITE)
            opts.setOpenAllSeries(True)

            process = ImportProcess(opts)

            try:
                process.execute()
            except:
                pass
            else:
                process.execute()

            try:
                imps = ImagePlusReader(process).openImagePlus()
            except:
                IJ.log(path + "\n" + "This file was not properly processed")
                pass

            else:
                dir_name = os.path.dirname(path)
                file_name = os.path.basename(os.path.splitext(path)[0])
                save_dir = os.path.join(dir_name, file_name)
                if not os.path.exists(save_dir):
                    os.makedirs(save_dir)

                imps = ImagePlusReader(process).openImagePlus()
                for i, imp in enumerate(imps):
                    save_path = os.path.join(save_dir, file_name + "_pos{}.tif".format(i + 1))

                    if not os.path.exists(save_path):
                        IJ.saveAsTiff(imp, save_path)
                        IJ.freeMemory()
                    else:
                        if overwrite:
                            IJ.saveAsTiff(imp, save_path)
                            IJ.freeMemory()
                        else:
                            pass



def get_ok():

    gd = GenericDialog("Caution")
    gd.addMessage("Do you want to overwrite the files ? ")
    gd.showDialog()
    return gd.wasOKed()

fs = get_file_list()

nd_files = [f for f in fs
            if f.endswith("nd") or f.endswith("nd2")]


trans_to_tif(nd_files, overwrite=False)

# If you want to overwrite, overwrite=True or
# overwrite=getOK() to open a dialog.