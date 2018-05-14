from aurigapy import *
from time import sleep
from time import gmtime, strftime


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def on_reading(value, timeout):
    print("%r > %r (%r)" % (timestamp(), value, timeout))


ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(usb)
print("Conectado")

sleep(2)

for i in range(100):
    r = ap.get_ultrasonic_reading(10 , on_reading)
    sleep(0.2)


sleep(1)
ap.reset_robot()
ap.close()
