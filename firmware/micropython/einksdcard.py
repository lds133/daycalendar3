"""
eink_sdcard.py
Bundles the SD card reader and the 7in5bc e-Paper panel behind a simple
init() / drawbmp() / finit() lifecycle, for MicroPython on the Raspberry
Pi Pico 2.

Requires on the Pico's filesystem (alongside this file):
    sdcard.py       - the MicroPython SD card driver
    epdconfig.py    - Pico port of the e-Paper hardware layer
    epd7in5bc.py    - e-Paper driver
    logging.py      - logging shim (only needed if your build lacks one)

BMP format supported - and why:
    8-bit indexed (256-color palette), uncompressed (BI_RGB), classic
    40-byte BITMAPINFOHEADER. This is the simplest BMP variant that can
    hold 3 distinct colors while staying byte-aligned per pixel (1 byte =
    1 pixel = 1 palette index), so there is no bit-shifting needed to read
    pixels - unlike 1bpp/4bpp packed formats. Only 3 palette entries are
    actually needed (white, black, red); any extra palette colors are
    ignored and unused indices simply won't appear in the image.

    To produce a compatible file with Pillow on a PC:
        from PIL import Image
        img = Image.open("art.png").convert("RGB")
        pal = Image.new("P", (1, 1))
        pal.putpalette([255,255,255, 0,0,0, 255,0,0] + [0] * (253 * 3))
        img.quantize(palette=pal, dither=Image.NONE).save(
            "image.bmp", "BMP"
        )

Rotation:
    Every BMP is rotated 90 degrees before being drawn (the panel is
    mounted in album/landscape orientation). ROTATION below is hardcoded
    to either 'CW' (clockwise) or 'CCW' (counterclockwise). After
    rotation the image's on-screen width equals its original height, and
    vice versa.

Alignment requirement (why the rotated width and each xpos must be
multiples of 8):
    The e-Paper frame buffer packs 8 horizontal pixels per byte. Since
    rotation is applied, the dimension that ends up horizontal on screen
    is the BMP's original HEIGHT - that value (not the BMP's width) is
    what must be a multiple of 8, together with xpos.
"""

import machine
import sdcard
import uos
import time
import epd7in5bc

# ------------------------------------------------------------------
# Hardcoded parameters
# ------------------------------------------------------------------
SD_MOUNT_POINT = "/sd"

# SD card SPI wiring (matches the known-working test_sdcard.py example)
SD_CS_PIN   = 17
SD_SCK_PIN  = 18
SD_MOSI_PIN = 19
SD_MISO_PIN = 16
SD_SPI_ID   = 0
SD_BAUD     = 1_000_000

# Rotation applied to every BMP before drawing. Must be 'CW' or 'CCW'.
ROTATION = 'CW'

# Reference colors used to classify each BMP palette entry
_WHITE = (255, 255, 255)
_BLACK = (0, 0, 0)
_RED   = (255, 0, 0)


# ------------------------------------------------------------------
# BMP helpers (module-level, no hardware state needed)
# ------------------------------------------------------------------
def _classify_color(r, g, b):
    """Map an arbitrary RGB palette entry to the nearest of white/black/red."""
    def dist2(c):
        return (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2
    best = min((_WHITE, _BLACK, _RED), key=dist2)
    if best is _WHITE:
        return 'W'
    elif best is _BLACK:
        return 'B'
    return 'R'


def _read_le(buf, offset, size):
    val = 0
    for i in range(size):
        val |= buf[offset + i] << (8 * i)
    return val


def _read_le_signed32(buf, offset):
    val = _read_le(buf, offset, 4)
    if val & 0x80000000:
        val -= 0x100000000
    return val


def _load_bmp_header(f):
    """Read and validate the BMP file header + palette. Leaves the file
    positioned at the start of the pixel data on return."""
    header = f.read(54)
    if header[0:2] != b'BM':
        raise ValueError("Not a BMP file")

    data_offset = _read_le(header, 10, 4)
    dib_size = _read_le(header, 14, 4)
    if dib_size != 40:
        raise ValueError("Only the 40-byte BITMAPINFOHEADER is supported")

    width = _read_le_signed32(header, 18)
    height = _read_le_signed32(header, 22)
    bpp = _read_le(header, 28, 2)
    compression = _read_le(header, 30, 4)
    if bpp != 8:
        raise ValueError("Only 8-bit indexed BMP is supported")
    if compression != 0:
        raise ValueError("Only uncompressed (BI_RGB) BMP is supported")

    top_down = height < 0
    height = abs(height)

    palette_len_bytes = data_offset - 54
    num_colors = palette_len_bytes // 4
    palette_raw = f.read(palette_len_bytes)

    palette = []
    for i in range(num_colors):
        b = palette_raw[i * 4 + 0]
        g = palette_raw[i * 4 + 1]
        r = palette_raw[i * 4 + 2]
        palette.append(_classify_color(r, g, b))

    f.seek(data_offset)

    return {
        "width": width,
        "height": height,
        "top_down": top_down,
        "palette": palette,
    }


def _bmp_row_size_bytes(width_px):
    # 8 bits per pixel, rows padded to a 4-byte boundary.
    return ((width_px * 8 + 31) // 32) * 4


def _read_rows_top_to_bottom(f, info):
    """Read every pixel row and return a list ordered so index 0 is
    always the visual TOP row of the image, regardless of how the file
    stored it (BMP rows are bottom-up unless the height field was
    negative, i.e. top-down)."""
    width = info["width"]
    height = info["height"]
    row_bytes = _bmp_row_size_bytes(width)

    rows_in_file_order = [f.read(row_bytes) for _ in range(height)]

    if info["top_down"]:
        return rows_in_file_order
    return list(reversed(rows_in_file_order))


def _rotated_pixel_position(sx, sy, width, height, rotation):
    """Map a source pixel (sx, sy) - 0-indexed, (0,0) at top-left of the
    BMP as authored - to its (dest_x, dest_y) position within the
    rotated image, whose size is (height, width)."""
    if rotation == 'CW':
        dest_x = height - 1 - sy
        dest_y = sx
    else:  # 'CCW'
        dest_x = sy
        dest_y = width - 1 - sx
    return dest_x, dest_y


# ------------------------------------------------------------------
# The object
# ------------------------------------------------------------------
class EinkSDCard:
    """Bundles the SD card reader and the 7in5bc e-Paper panel behind a
    minimal init() / drawbmp() / finit() lifecycle."""

    def __init__(self):
        self.epd = None
        self.black_buf = None
        self.red_buf = None
        self._sd_mounted = False

    def init(self,isclear=True):
        """Mount the SD card and initialize + clear the e-Paper panel."""
        cs = machine.Pin(SD_CS_PIN, machine.Pin.OUT)
        spi = machine.SPI(
            SD_SPI_ID,
            baudrate=SD_BAUD,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=machine.SPI.MSB,
            sck=machine.Pin(SD_SCK_PIN),
            mosi=machine.Pin(SD_MOSI_PIN),
            miso=machine.Pin(SD_MISO_PIN),
        )
        time.sleep_ms(100)
        sd = sdcard.SDCard(spi, cs)
        time.sleep_ms(100)
        vfs = uos.VfsFat(sd)
        uos.mount(vfs, SD_MOUNT_POINT)
        time.sleep_ms(100)
        self._sd_mounted = True

        print("Initializing e-Paper...")
        self.epd = epd7in5bc.EPD()
        if self.epd.init() != 0:
            raise RuntimeError("EPD init failed - check wiring / epdconfig pin numbers")

        if isclear:
            print("Clearing display...")
            self.epd.Clear()

        screen_row_bytes = epd7in5bc.EPD_WIDTH // 8
        self.black_buf = bytearray([0xFF for _ in range(screen_row_bytes * epd7in5bc.EPD_HEIGHT)])
        self.red_buf = bytearray([0xFF for _ in range(screen_row_bytes * epd7in5bc.EPD_HEIGHT)])

    def drawbmp(self, filename, xpos, ypos):
        """Read the BMP at `filename` from the SD card, rotate it per
        ROTATION, and draw it into the internal frame buffers with its
        top-left corner at (xpos, ypos). Can be called multiple times to
        compose several images before finit() sends them to the panel."""
        if self.black_buf is None or self.red_buf is None:
            raise RuntimeError("call init() before drawbmp()")

        screen_row_bytes = epd7in5bc.EPD_WIDTH // 8

        print("Reading", filename)
        with open(filename, "rb") as f:
            info = _load_bmp_header(f)
            img_w = info["width"]
            img_h = info["height"]
            print("BMP is {}x{}, rotating {}".format(img_w, img_h, ROTATION))

            # After a 90-degree rotation the on-screen width is the BMP's
            # original height, and the on-screen height is the BMP's
            # original width.
            rotated_w = img_h
            rotated_h = img_w

            #if rotated_w % 8 != 0:
            #    raise ValueError(
            #        "BMP height ({}) must be a multiple of 8 (it becomes "
            #        "the on-screen width after rotation)".format(img_h)
            #    )
            #if xpos % 8 != 0:
            #    raise ValueError("xpos must be a multiple of 8")
            if xpos + rotated_w > epd7in5bc.EPD_WIDTH:
                raise ValueError("Rotated image doesn't fit horizontally at xpos")
            if ypos + rotated_h > epd7in5bc.EPD_HEIGHT:
                raise ValueError("Rotated image doesn't fit vertically at ypos")

            palette = info["palette"]
            rows = _read_rows_top_to_bottom(f, info)

            for sy in range(img_h):
                row_data = rows[sy]
                for sx in range(img_w):
                    color = palette[row_data[sx]]
                    if color == 'W':
                        continue  # buffers start all-white already

                    dest_x, dest_y = _rotated_pixel_position(sx, sy, img_w, img_h, ROTATION)
                    screen_x = xpos + dest_x
                    screen_y = ypos + dest_y

                    byte_index = screen_y * screen_row_bytes + (screen_x // 8)
                    bit_mask = 0x80 >> (screen_x % 8)
                    if color == 'B':
                        self.black_buf[byte_index] &= (~bit_mask) & 0xFF
                    else:  # 'R'
                        self.red_buf[byte_index] &= (~bit_mask) & 0xFF

    def getfiles(self, dirstr):
        """Return a list of file/directory names in `dirstr` on the
        mounted SD card (e.g. getfiles("/sd") or getfiles("/sd/pics"))."""
        if not self._sd_mounted:
            raise RuntimeError("call init() before getfiles()")
        return uos.listdir(dirstr)



    def finit(self):
        """Unmount the SD card, send the composed buffers to the
        e-Paper, and put the panel to sleep."""
        if self._sd_mounted:
            uos.umount(SD_MOUNT_POINT)
            self._sd_mounted = False

        print("Sending buffers to e-Paper...")
        self.epd.display(self.black_buf, self.red_buf)

        print("Sleeping display in 5s...")
        time.sleep(5)
        self.epd.sleep()
        print("Done. Display is in deep sleep.")

### END OF FILE ###