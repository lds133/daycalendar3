"""
test_sdcard_bmp_eink.py
Minimal test: read a BMP from the SD card and draw it on the e-Paper
display at a fixed X,Y position.

Requires on the Pico's filesystem (alongside this file):
    sdcard.py       - the MicroPython SD card driver (same one used by the
                       working test_sdcard.py example)
    epdconfig.py    - Pico port of the e-Paper hardware layer
    epd7in5bc.py    - e-Paper driver
    logging.py      - logging shim (only needed if your build lacks one)

BMP format used - and why:
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

Alignment requirement (why X, width must be multiples of 8):
    The e-Paper frame buffer packs 8 horizontal pixels per byte. Making
    both IMG_X and the image width multiples of 8 means every destination
    byte maps to a whole, non-overlapping run of 8 source pixels, so each
    row can be written as plain byte slices into the frame buffer with no
    partial-byte merging.
"""

import machine
import sdcard
import uos
import time
import epd7in5bc

# ------------------------------------------------------------------
# Hardcoded parameters
# ------------------------------------------------------------------
BMP_PATH = "/sd/image.bmp"

# Destination position on the e-Paper screen (top-left corner of the
# image). Both must be multiples of 8 - see note above.
IMG_X = 16
IMG_Y = 8

# SD card SPI wiring (matches the known-working test_sdcard.py example)
SD_CS_PIN   = 17
SD_SCK_PIN  = 18
SD_MOSI_PIN = 19
SD_MISO_PIN = 16
SD_SPI_ID   = 0
SD_BAUD     = 1_000_000

# Reference colors used to classify each BMP palette entry
_WHITE = (255, 255, 255)
_BLACK = (0, 0, 0)
_RED   = (255, 0, 0)


# ------------------------------------------------------------------
# BMP helpers
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


def load_bmp_header(f):
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


def _draw_bmp_row(row_data, palette, black_row, red_row, width_px):
    """Set bits for one image row into byte rows that start all-white
    (0xFF). Bit convention matches epd7in5bc.display():
        white -> black bit 1, red bit 1  (default, nothing to clear)
        black -> black bit 0, red bit 1
        red   -> black bit 1, red bit 0
    """
    for x in range(width_px):
        color = palette[row_data[x]]
        if color == 'W':
            continue
        byte_i = x // 8
        bit_mask = 0x80 >> (x % 8)
        if color == 'B':
            black_row[byte_i] &= (~bit_mask) & 0xFF
        else:  # 'R'
            red_row[byte_i] &= (~bit_mask) & 0xFF


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------
def main():
    # ---- Mount SD card ----
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
    uos.mount(vfs, "/sd")
    time.sleep_ms(100)

    screen_row_bytes = epd7in5bc.EPD_WIDTH // 8
    black_buf = bytearray([0xFF for _ in range(screen_row_bytes * epd7in5bc.EPD_HEIGHT)])
    red_buf = bytearray([0xFF for _ in range(screen_row_bytes * epd7in5bc.EPD_HEIGHT)])

    print("Reading", BMP_PATH)
    with open(BMP_PATH, "rb") as f:
        info = load_bmp_header(f)
        img_w = info["width"]
        img_h = info["height"]
        print("BMP is {}x{}".format(img_w, img_h))

        # ---- Validate alignment / bounds ----
        if img_w % 8 != 0:
            raise ValueError("Image width must be a multiple of 8")
        if IMG_X % 8 != 0:
            raise ValueError("IMG_X must be a multiple of 8")
        if IMG_X + img_w > epd7in5bc.EPD_WIDTH:
            raise ValueError("Image doesn't fit horizontally at IMG_X")
        if IMG_Y + img_h > epd7in5bc.EPD_HEIGHT:
            raise ValueError("Image doesn't fit vertically at IMG_Y")

        img_row_bytes = img_w // 8
        bmp_row_bytes = _bmp_row_size_bytes(img_w)
        x_byte_offset = IMG_X // 8
        palette = info["palette"]

        for y in range(img_h):
            row_data = f.read(bmp_row_bytes)  # includes any BMP row padding
            screen_row = IMG_Y + (y if info["top_down"] else (img_h - 1 - y))

            black_row = bytearray([0xFF for _ in range(img_row_bytes)])
            red_row = bytearray([0xFF for _ in range(img_row_bytes)])
            _draw_bmp_row(row_data, palette, black_row, red_row, img_w)

            dest_start = screen_row * screen_row_bytes + x_byte_offset
            black_buf[dest_start:dest_start + img_row_bytes] = black_row
            red_buf[dest_start:dest_start + img_row_bytes] = red_row

    uos.umount("/sd")

    print("Initializing e-Paper...")
    epd = epd7in5bc.EPD()
    if epd.init() != 0:
        print("EPD init failed - check wiring / epdconfig pin numbers")
        return

    print("Clearing display...")
    epd.Clear()

    print("Drawing image at ({}, {})...".format(IMG_X, IMG_Y))
    epd.display(black_buf, red_buf)

    print("Sleeping display in 5s...")
    time.sleep(5)
    epd.sleep()
    print("Done. Display is in deep sleep.")


if __name__ == "__main__":
    main()

### END OF FILE ###
