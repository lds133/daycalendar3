from PIL import Image
img = Image.new(mode="RGB", size=(256, 256))
#img = Image.open("art.png").convert("RGB")
pal = Image.new("P", (1, 1))
pal.putpalette([255,255,255, 0,0,0, 255,0,0] + [0] * (253 * 3))
img.quantize(palette=pal, dither=Image.NONE).save("image.bmp", "BMP")