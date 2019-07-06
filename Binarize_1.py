from ij import IJ, Prefs
from ij.plugin.filter import BackgroundSubtracter

Prefs.blackBackground = True
imp = IJ.getImage()



binimp = imp.duplicate()
bs = BackgroundSubtracter()
ip = binimp.getProcessor()
bs.rollingBallBackground(ip, 15, False, False, False, True, True)

IJ.run(binimp, "Unsharp Mask...", "radius=2 mask=0.9")

def smooth(n=1):
    for i in range(n):
        IJ.run(binimp, "Smooth", "")

smooth(10)
Prefs.blackBackground = True
IJ.setAutoThreshold(binimp, "Moments dark")
IJ.run(binimp, "Make Binary", "thresholded remaining")

smooth(12)

IJ.run(binimp, "Unsharp Mask...", "radius=2 mask=0.9")

IJ.setAutoThreshold(binimp, "Moments white")
IJ.run(binimp, "Make Binary", "thresholded remaining")

IJ.run(binimp, "Erode", "")
IJ.run(binimp, "Dilate", "")

binimp.show()

IJ.run(binimp, "Analyze Particles...", "size=300-Infinity circularity=0.65-1.00 exclude clear add")



"""
IJ.run(binimp, "Erode", "")

binimp.show()
IJ.run(binimp, "Analyze Particles...", "size=320-Infinity circularity=0.7-1.00 exclude clear add")
"""
"""
IJ.run(binimp, "Make Binary", "thresholded remaining")

smooth(10)
IJ.setAutoThreshold(binimp, "Moments dark")
IJ.run(binimp, "Make Binary", "thresholded remaining")
"""
"""
IJ.setAutoThreshold(binimp, "Moments dark")
IJ.run(binimp, "Make Binary", "thresholded remaining")
# Prefs.blackBackground = True
# IJ.setAutoThreshold(binimp, "Otsu dark")
# IJ.run(binimp, "Make Binary", "thresholded remaining")

"""
"""
EDM().toWatershed(binimp.getProcessor())
"""
"""
smooth(20)

IJ.setAutoThreshold(binimp, "Otsu dark")

# IJ.run(imp, "Watershed", "")

# IJ.run(imp, "Analyze Particles...", "size=350-Infinity circularity=0.7-1.00 exclude clear add")