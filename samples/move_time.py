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

sleep(2)

start = time()

#A (-51,51) de velocidad durante 20 segundos recorren 318cm
#Durante 1 segundo a esa velocidad se recorreria 15,9cm
#Por tanto por cada unidad de velocidad se recorre  0,311764706cm por segundo

#Asumiré por redondeo que realmente por cada unidad de velocidad se recorre  0,312cm

while time() - start < 20:
    ap.set_encoder_motor_rotate(1, -51)
    ap.set_encoder_motor_rotate(2, 51)


ap.reset_robot()
ap.close()
