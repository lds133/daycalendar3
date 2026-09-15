from PIL import Image



def CreateImageTemplate(width,height):

    img = Image.new("RGB", (width,height), (255, 255, 255))
    pal = Image.new("P", (1, 1))
    pal.putpalette([ 0,0,0, 255,0,0,255,255,255] + [0] * (253 * 3))
    return img.quantize(palette=pal, dither=Image.NONE)
    
    
