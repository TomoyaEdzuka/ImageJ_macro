# import glob
# import os
#
# from ij import IJ, ImagePlus
# from ij.gui import Roi, Overlay
# from ij.io import DirectoryChooser
# from ij.plugin import StackCombiner
# from ij.plugin.frame import RoiManager
# from ij.process import StackProcessor
# from java.awt import Color
#
# from ij import WindowManager
#
# def rm_ext(file_name):
#     """
#     Remove extension of file_name: str
#     """
#     while True:
#         file_name, ext = os.path.splitext(file_name)
#         if ext == '':
#             break
#     return file_name
#
#
# def get_file_info(imp=IJ.getImage()):
#     """
#     get abstract directory and
#     base filename with no extension
#     """
#     img_dir = imp.getOriginalFileInfo().directory
#     img_file = imp.getOriginalFileInfo().fileName
#     os.path.splitext(img_file)
#     name = rm_ext(img_file)
#
#     return img_dir, name
#
#
# # def get_numeric_str(path, pattern = '.([0-9]).'):
# #
# #     result_list = [re.findall(pattern, string) for string in l]
# #     def flatten(nested):
# #         """2重リストを解消"""
# #         return [item for inner in nested for item in inner]
# #     result_l = flatten(result_list)
# #     return int(max(result_l)) + 1
#
#
# def make_new_folder(new_folder, imp=IJ.getImage()):
#     dir = imp.getOriginalFileInfo().directory
#     if dir:
#         new_dir = os.path.join(dir, new_folder)
#         if not os.path.exists(new_dir):
#             os.makedirs(new_dir)
#     else:
#         return
#
#
# def make_roi_dir(img_dir, name):
#     roi_dir = os.path.join(img_dir, "{}_RoiSets".format(name))
#     if not os.path.exists(roi_dir):
#         os.makedirs(roi_dir)
#         return roi_dir
#     else:
#         return roi_dir
#
#
# def make_roi_path(roi_dir, name):
#     roi_paths = glob.glob(roi_dir + os.sep + name + "*" + ".zip")
#     file_id_numbers = [extract_before_ext_num(roi_path, "zip") for roi_path in roi_paths]
#     max_id = max(file_id_numbers)
#     if file_id_numbers:
#         save_roi_path = os.path.join(roi_dir, "{0}_RoiSet_{1}.zip".format(name, max_id + 1))
#     else:
#         save_roi_path = os.path.join(roi_dir, "{0}_RoiSet_1.zip".format(name))
#     return save_roi_path
#
#
# def save_roi_set():
#     img_dir, name = get_file_info()
#     roi_dir = make_roi_dir(img_dir, name)
#     roi_path = make_roi_path(roi_dir, name)
#
#     rm = RoiManager().getInstance()
#     rm.deselect()
#     rm.runCommand("Save", roi_path)
#
#     rm.runCommand("delete")
#
#
# def roi_to_overlay(imp=IJ.getImage(), rm=RoiManager().getInstance()):
#     Roi.setColor(Color.blue)
#     rm = RoiManager().getInstance()
#     rm.deselect()
#
#     Roi.setColor(Color.yellow)
#
#     ol = imp.getOverlay()
#     ol.setStrokeColor(Color.blue)
#     if ol is None:
#         ol = Overlay()
#     for roi in rm.getRoisAsArray():
#         ol.add(roi)
#         imp.setOverlay(ol)
#
#
# # integrated_combine(scale = 0.25, col = 6)
# def save_imp(new_imp, original_imp=IJ.getImage(), prefix="combined", save_func=IJ.save,
#              overwrite=True):  # imp :ImagePlus, path: str
#
#     dir_name = original_imp.getOriginalFileInfo().directory
#     file_name = original_imp.getOriginalFileInfo().fileName
#     base_file_name, ext = os.path.splitext(file_name)
#
#     if dir_name:
#         new_dir = os.path.join(dir_name, "{}_{}".format(dir_name, prefix))
#         if not os.path.exists(new_dir):
#             os.makedirs(new_dir)
#
#         if overwrite == True:
#             paths = glob.glob(new_dir + os.sep + ":.tif")
#             file_nums = [extract_before_ext_num(path) for path in paths]
#             if not file_nums:
#                 save_file_name = "{0}_{1}_1.{2}".format(base_file_name, prefix, ext)
#                 save_path = os.path.join(new_dir, save_file_name)
#                 save_func(new_imp, save_path)
#
#                 return
#             else:
#                 max_num = max(file_nums)
#                 save_file_name = "{0}_{1}_{2}.{3}".format(base_file_name, prefix, max_num, ext)
#                 save_path = os.path.join(new_dir, save_file_name)
#                 save_func(new_imp, save_path)
#
#
#         else:
#             return
#
#
def extract_before_ext_num(file_path, extension=r".*"):
    """
    Hit the number at the end of file name
    Return this value by converting str to int
    file_path = "path = '/Users/Edzuka/1212ug_1123.png'"
    In this case, equivalent to 1123
    """
    import re
    pattern = re.compile(r".*?(?P<number>[0-9]+)\." + extension)
    match = pattern.match(file_path)
    if match:
        file_number_str = match.group("number")
        file_number = int(file_number_str)
        return file_number
    else:
        error_content = "File name does not end with number or extension is not {}".format(extension)
        raise Exception(error_content)


# def multislice(imp=IJ.getImage()):
#     parent_dir = imp.getOriginalFileInfo().directory
#     imp_file_name = imp.getOriginalFileInfo().fileName
#     imp_title, ext = os.path.splitext(imp_file_name)
#     save_dir = os.path.join(parent_dir, imp_title + "_kymographs")
#
#     if not os.path.exists(save_dir):
#         os.makedirs(save_dir)
#
#     paths = glob.glob(save_dir + os.sep + "*.tif")
#     file_nums = [extract_before_ext_num(path) for path in paths]
#     if not file_nums:
#         max_num = 0
#     else:
#         max_num = max(file_nums)
#
#     rm = RoiManager().getInstance()
#     for i, roi in enumerate(rm.getRoisAsArray()):
#         imp.setRoi(roi)
#         IJ.run(imp, "Reslice [/]...", "output=1.000 slice_count=1")
#         kymo_imp = WindowManager.getCurrentImage()
#         save_title = "{0}_kymographs_{1}{2}".format(imp_title, i+max_num+1, ext)
#         save_path = os.path.join(save_dir, save_title)
#         IJ.save(kymo_imp, save_path)
#
#
#     titles = WindowManager.getImageTitles()
#
#     for title in titles:
#         imp = WindowManager.getImage(title)
#         if "Reslice" in title:
#             imp.close()
#
#
# def get_start_end_coord(roi):
#     imp = IJ.getImage()
#     IJ.run(imp, "Set Scale...", "distance=1 known=1 pixel=1 unit=pixel")
#     roi.setImage(imp)
#     if roi.getType() == roi.LINE:
#         polygon = roi.getFloatPolygon()
#
#         xs = polygon.xpoints
#         ys = polygon.ypoints
#
#         x_start = xs[0]
#         x_end = xs[1]
#
#         y_start = ys[0]
#         y_end = ys[1]
#
#     elif roi.getType() == roi.POLYLINE:
#         polygon = roi.getFloatPolygon()
#
#         xs = polygon.xpoints
#         ys = polygon.ypoints
#
#         x_start = xs[0]
#         x_end = xs[-1]
#
#         y_start = ys[0]
#         y_end = ys[-1]
#
#     else:
#         return
#
#     return x_start, x_end, y_start, y_end
#
#
# def write_csv(col_names, *data):
#     import csv
#     # col_name: list
#     for_csv_row = zip(*data)
#
#     csv_path = os.path.join(get_file_info()[0], get_file_info()[1] + "_analyze.csv")
#
#     # ファイルに内容がある場合は何もせず, 内容がないときだけカラムを書き込む
#     with open(csv_path, "a") as f1:
#         with open(csv_path, "r") as f2:
#             s = f2.read()
#         if s == "":
#             with open(csv_path, "w") as f3:
#                 writer = csv.writer(f3)
#                 writer.writerow(col_names)
#
#     # 上書きモードで値を書き込む
#     with open(csv_path, "a") as f:
#         writer = csv.writer(f)
#         writer.writerows(for_csv_row)
#
#     # table上に表示する
#     op = Opener()
#     op.openTable(csv_path)
#
#
# def get_file_list():
#     parent_dir = DirectoryChooser("Choose").getDirectory()
#
#     if parent_dir is not None:
#         file_list = glob.glob(parent_dir + "*")
#         return file_list
#     else:
#         pass
#
#
# def resize(imp, scale):
#     width = imp.getWidth() * scale
#     height = imp.getHeight() * scale
#     stack_processor = StackProcessor(imp.getImageStack())
#     new_stack = stack_processor.resize(int(width), int(height))
#     imp = ImagePlus("new", new_stack)
#     return imp
#
#
# def combine_images(imps, direction="horizontally"):
#     stack_combiner = StackCombiner()
#     img_stack1 = imps[0].getImageStack()
#     img_stack2 = imps[1].getImageStack()
#
#     if direction == "horizontally":
#         combined_stack = stack_combiner.combineHorizontally(img_stack1, img_stack2)
#         for imp in imps[2:]:
#             img_stack = imp.getImageStack()
#             combined_stack = stack_combiner.combineHorizontally(combined_stack, img_stack)
#
#     if direction == "vertically":
#         combined_stack = stack_combiner.combineVertically(img_stack1, img_stack2)
#         for imp in imps[2:]:
#             img_stack = imp.getImageStack()
#             combined_stack = stack_combiner.combineVertically(combined_stack, img_stack)
#
#     combined_imp = ImagePlus("combined_image", combined_stack)
#     return combined_imp
#
#
# # create a empty image with the same dimensions, bitdepth
# def create_empty_imp(imp):
#     dims = imp.getDimensions()
#     depth = imp.getBitDepth()
#     dims = list(dims)
#     dims.append(depth)
#     new_imp = IJ.createHyperStack("new", *dims)
#
#     return new_imp
#
#
# def separate_imps(imps, n):
#     outer_list = []
#     inner_list = []
#     if n > len(imps):
#         n = len(imps)
#
#
#     for i, imp1 in enumerate(imps):
#         inner_list.append(imp1)
#         if len(inner_list) == n:
#             outer_list.append(inner_list)
#             inner_list = []
#         if i + 1 == len(imps) and inner_list != []:
#             empty_imp = create_empty_imp(imp1)
#             while n - len(inner_list) > 0:
#                 inner_list.append(empty_imp)
#             outer_list.append(inner_list)
#     return outer_list
#
#
# def integrated_combine(scale, col):
#     fl = get_file_list()
#     imps = [IJ.openImage(f) for f in fl]
#     resized_imps = [resize(imp, scale) for imp in imps]
#     del imps
#     imps_list = separate_imps(resized_imps, col)
#     del resized_imps
#     combined_imps = [combine_images(imps) for imps in imps_list]
#     vertical_combined_imp = combine_images(combined_imps, "vertically")
#     del combined_imps
#     vertical_combined_imp.show()
#
# integrated_combine(1, 2)


def make_increment_path(target_dir, file_title, ext):
    import os
    import glob

    paths = glob.glob(target_dir + os.sep + file_title + "*." + ext)
    if paths:
        path_nums = [extract_before_ext_num(path) for path in paths]
        if path_nums:
            max_num = max(path_nums)
        else:
            max_num = 1
        return os.path.join(target_dir, "{0}_{1}.{2}".format(file_title, max_num + 1, ext))
    else:
        return


p = make_increment_path(target_dir="/Users/Edzuka/Desktop/temp1/664-2/664-2_pos1_kymographs",
                        file_title="664-2_pos1_kymographs",
                        ext="tif")
print(p)

l = ["664-2_pos1_kymographs_1.tif",
     "664-2_pos1_kymographs_2.tif",
     "664-2_pos1_kymographs_3.tif",
     "664-2_pos1_kymographs_4.tif",
     "664-2_pos1_kymographs_5.tif",
     "664-2_pos1_kymographs_6.tif",
     "664-2_pos1_kymographs_7.tif",
     "664-2_pos1_kymographs_8.tif",
     "664-2_pos1_kymographs_9.tif",
     "664-2_pos1_kymographs_10.tif",
     "664-2_pos1_kymographs_11.tif",
     "664-2_pos1_kymographs_12.tif",
     "664-2_pos1_kymographs_13.tif",
     "664-2_pos1_kymographs_14.tif",
     "664-2_pos1_kymographs_15.tif",
     "664-2_pos1_kymographs_16.tif",
     "664-2_pos1_kymographs_17.tif",
     "664-2_pos1_kymographs_18.tif",
     "664-2_pos1_kymographs_19.tif",
     "664-2_pos1_kymographs_20.tif"]
