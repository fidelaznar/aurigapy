from aurigapy import *
from time import sleep, time
from time import gmtime, strftime


def print_ts(s):
    ts = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("%r| %r" % (ts, s))



ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(bluetooth)
print("Conectado")
sleep(3)
start = time()

i = 0

#Asi obtengo una frecuencia de unas 11 iteraciones por segundo, casi los 100ms estimados
while time() - start < 14:


    ap.set_encoder_motor_rotate(1, -51)
    ap.set_encoder_motor_rotate(2, 30)
    #sleep(0.1)

    i += 1

ap.reset_robot()
ap.close()
