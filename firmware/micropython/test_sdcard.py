import machine
import sdcard
import uos
import time

# Assign chip select (CS) pin (and start it high)
cs = machine.Pin(17, machine.Pin.OUT)

# Intialize SPI peripheral (start with 1 MHz)
spi = machine.SPI(0,
                  baudrate=100000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  firstbit=machine.SPI.MSB,
                  sck=machine.Pin(18),
                  mosi=machine.Pin(19),
                  miso=machine.Pin(16))

time.sleep_ms(100)
# Initialize SD card
sd = sdcard.SDCard(spi, cs)

time.sleep_ms(100)
# Mount filesystem
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")
time.sleep_ms(100)

# Create a file and write something to it
with open("/sd/test01.txt", "w") as file:
    file.write("Hello, SD World!\r\n")
    file.write("This is a test\r\n")

# Open the file we just created and read from it
with open("/sd/test01.txt", "r") as file:
    data = file.read()
    print(data)
    