from ij import IJ, ImagePlus, ImageStack

imp = IJ.getImage()

nframe = imp.getNFrames()

img_stack = ImageStack()

for i in range(nframe):
    imp.setT(i + 1)
    ip = imp.getProcessor()   
    if i % 6 == 0:
        img_stack.addSlice(ip)


new_imp = ImagePlus("new", img_stack)  
new_imp.show()
    
   
    
    
   