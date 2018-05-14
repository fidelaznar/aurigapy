# coding=utf-8
from aurigapy import *
from time import *
from time import gmtime, strftime

ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


print("%r Conectando..." % timestamp())
ap.connect(bluetooth)
print("%r Conectado!" % timestamp())

#360 grados son 1003 en el Dashing Raptor
d = round(1003/2)

print("Rotate 180...")
ap.move_to(command="right", degrees=d, speed=125)
sleep(1)
# print("Rotate -180...")
ap.move_to(command="left", degrees=d, speed=125)
print("End Rotating...")
print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
