"""
test_epd.py
Simple MicroPython test for the Pico-ported epd7in5bc driver.

Copy epdconfig.py, epd7in5bc.py, logging.py, and this file onto the Pico's
filesystem (flat, same directory - e.g. via Thonny or `mpremote cp`), then
run this file on the board.

This test avoids PIL/Pillow (not available on MicroPython) by building the
black/red bitmap buffers manually instead of using getbuffer()/getbuffer_ex().
"""

import time
import epd7in5bc

WIDTH = epd7in5bc.EPD_WIDTH    # 640
HEIGHT = epd7in5bc.EPD_HEIGHT  # 384
ROW_BYTES = WIDTH // 8


def make_tricolor_stripe_buffers(stripe_height=40):
    """Build black+red buffers that together draw repeating
    white / black / red horizontal stripes.

    Per the driver's send logic in display():
        red bit  == 0  -> red pixel   (black bit is ignored)
        red bit  == 1, black bit == 0 -> black pixel
        red bit  == 1, black bit == 1 -> white pixel
    """
    black_buf = bytearray(ROW_BYTES * HEIGHT)
    red_buf = bytearray(ROW_BYTES * HEIGHT)

    for y in range(HEIGHT):
        stripe = (y // stripe_height) % 3   # 0=white, 1=black, 2=red
        if stripe == 0:                     # white
            black_byte, red_byte = 0xFF, 0xFF
        elif stripe == 1:                   # black
            black_byte, red_byte = 0x00, 0xFF
        else:                               # red
            black_byte, red_byte = 0xFF, 0x00

        row_start = y * ROW_BYTES
        for i in range(ROW_BYTES):
            black_buf[row_start + i] = black_byte
            red_buf[row_start + i] = red_byte

    return black_buf, red_buf


def make_blank_buffer(fill=0xFF):
    return bytearray([fill for _ in range(ROW_BYTES * HEIGHT)])


def main():
    print("Initializing e-Paper (7in5bc) on Pico...")
    epd = epd7in5bc.EPD()

    if epd.init() != 0:
        print("EPD init failed - check wiring / epdconfig pin numbers")
        return

    print("Clearing display...")
    epd.Clear()
    time.sleep(1)

    print("Sending white/black/red striped test pattern...")
    black_buf, red_buf = make_tricolor_stripe_buffers(stripe_height=40)
    epd.display(black_buf, red_buf)

    print("Test pattern sent. Sleeping display in 5s...")
    time.sleep(5)

    epd.sleep()
    print("Done. Display is in deep sleep.")


if __name__ == "__main__":
    main()

### END OF FILE ###