from aurigapy import *
from time import gmtime, strftime

def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(bluetooth)
print("Conectado")

for i in range(10):
    ap.play_sound(sound=i * 5 + 131, duration_ms=100)

ap.reset_robot()
print("Closing")
ap.close()
