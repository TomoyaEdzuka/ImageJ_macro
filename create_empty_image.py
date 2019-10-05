from ij import IJ, ImagePlus

# create a empty image with the same dimensions, bitdepth
imp = IJ.getImage()
dims = imp.getDimensions()
depth = imp.getBitDepth()
dims = list(dims)
dims.append(depth)

new_imp = IJ.createHyperStack("new", *dims)
new_imp.show()

