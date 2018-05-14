from aurigapy import *
from time import sleep

ap = AurigaPy()

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1410"

ap.connect(usb)
print("Conectado")
sleep(2)
print("Rot 1")
ap.set_encoder_motor_rotate(2, 360, 200)

sleep(2)
print("Rot?")
print(ap.get_encoder_motor_degrees(2))

print("Rot 2")
ap.set_encoder_motor_rotate(2, -360, 200)
sleep(2)
print("Rot?")
print(ap.get_encoder_motor_degrees(2))


ap.reset_robot()
ap.close()
