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

#Rueda 6cm de diámetro, longitud: 2*pi*3 = 18.85 cada 360 grados. Por grado
#se avanza 0,052361111.  Por cm se avanzan 19,098143236 grados.
#Por tanto para avanzar un metro hay que rodar 1910 grados


print("Moving 1m...")
ap.move_to(command="forward", degrees=1910, speed=125)
print("End Moving...")
print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
