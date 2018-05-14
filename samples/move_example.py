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
sleep(3)
print("%r Conectado!" % timestamp())

# speed [0,255]
ap.set_command(command="forward", speed=40)
sleep(3)
ap.set_command(command="right", speed=40)
sleep(3)
ap.set_command(command="left", speed=80)
sleep(1.5)
ap.set_command(command="backward", speed=80)
sleep(1)

print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
