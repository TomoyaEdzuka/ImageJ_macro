from ij import IJ, ImagePlus
from ij.io import DirectoryChooser
from ij.plugin import StackCombiner
from ij.process import ImageProcessor, StackProcessor
import os
import glob


def get_file_list():
    parent_dir = DirectoryChooser("Choose").getDirectory()

    if parent_dir is not None:
        file_list = glob.glob(parent_dir + "*")
        return file_list
    else:
        pass

def resize(imp, scale):
    width = imp.getWidth()*scale
    height = imp.getHeight()*scale
    stack_processor = StackProcessor(imp.getImageStack())
    new_stack = stack_processor.resize(int(width), int(height))
    imp = ImagePlus("new", new_stack)
    return imp


def combine_images(imps, direction = "horizontally"):
    stack_combiner = StackCombiner()
    img_stack1 = imps[0].getImageStack()
    img_stack2 = imps[1].getImageStack()
    
    if direction == "horizontally":
        combined_stack = stack_combiner.combineHorizontally(img_stack1, img_stack2)
        for imp in imps[2:]:
            img_stack = imp.getImageStack()
            combined_stack = stack_combiner.combineHorizontally(combined_stack, img_stack)
    
    if direction == "vertically":
        combined_stack = stack_combiner.combineVertically(img_stack1, img_stack2)
        for imp in imps[2:]:
            img_stack = imp.getImageStack()
            combined_stack = stack_combiner.combineVertically(combined_stack, img_stack)
    
    combined_imp = ImagePlus("combined_image", combined_stack)
    return combined_imp


# create a empty image with the same dimensions, bitdepth
def create_empty_imp(imp):
    dims = imp.getDimensions()
    depth = imp.getBitDepth()
    dims = list(dims)
    dims.append(depth)
    new_imp = IJ.createHyperStack("new", *dims)

    return new_imp

def separate_imps(imps, n):
    outer_list = []
    inner_list = []
    for i, imp1 in enumerate(imps):
        inner_list.append(imp1)
        if len(inner_list) == n:
            outer_list.append(inner_list)
            inner_list = []
        if i + 1 == len(imps) and inner_list != []:
            empty_imp = create_empty_imp(imp1)
            while n - len(inner_list) > 0:            
                inner_list.append(empty_imp)
            outer_list.append(inner_list)
    return outer_list



def integrated_combine(scale, col):
    fl = get_file_list()
    imps = [IJ.openImage(f) for f in fl]
    resized_imps = [resize(imp, scale) for imp in imps]
    del imps
    imps_list = separate_imps(resized_imps, col)
    del resized_imps
    combined_imps = [combine_images(imps) for imps in imps_list]
    vertival_combined_imp = combine_images(combined_imps, "vertically")
    del combined_imps
    vertival_combined_imp.show()

integrated_combine(scale = 0.25, col = 3)

IJ.freeMemory()
