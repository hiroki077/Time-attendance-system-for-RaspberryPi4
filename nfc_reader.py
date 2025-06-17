from machine import SPI, Pin
from mfrc522 import MFRC522

sck = Pin(6, Pin.OUT)
mosi = Pin(7, Pin.OUT)
miso = Pin(4, Pin.OUT)
cs = Pin(5, Pin.OUT)
rst = Pin(18, Pin.OUT)
spi = SPI(0, baudrate=100000, polarity=0, phase=0, sck=sck, mosi=mosi, miso=miso)
rdr = MFRC522(spi, cs, rst)

def read_uid():
    (stat, tag_type) = rdr.request(rdr.REQIDL)
    if stat == rdr.OK:
        (stat, raw_uid) = rdr.anticoll()
        if stat == rdr.OK:
            uid = "0x" + "".join(["%02x" % b for b in raw_uid])
            return uid
    return None



