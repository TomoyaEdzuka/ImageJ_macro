from ij import IJ, ImagePlus
from ij.process import StackProcessor


def resize(imp, scale):
    width = imp.getWidth()*scale
    height = imp.getHeight()*scale
    stack = imp.getImageStack()
    ip = imp.getProcessor()
    stack_processor = StackProcessor(stack)
    new_stack = stack_processor.resize(int(width), int(height))
    imp = ImagePlus("new", new_stack)
    return imp

imp1 = IJ.getImage()
resized_imp = resize(imp=imp1, scale=0.25)
resized_imp.show()

