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
ap.connect(usb)
print("%r Conectado!" % timestamp())


print("Encoder 1 at: ", ap.get_encoder_motor_degrees(1))

# speed [0,255]
print("Moving right...")
ap.set_command_until(command="right", degrees=1000, speed=125)

sleep(1)

# Espero a que termine
vel = 0.01
while vel != 0:
    t = ap.get_encoder_motor_speed(1)
    if t is not None:
        vel = t
    t = ap.get_encoder_motor_speed(2)
    if t is not None:
        vel += t
    print(vel)
    sleep(0.1)
print("Terminó el mov.")

print("Encoder 1 at: ", ap.get_encoder_motor_degrees(1))

print("Moving left")
ap.set_command_until(command="left", degrees=1460, speed=125)
sleep(2)

# Espero a que termine ahora sin mostrar la vel
vel = 0.01
while vel != 0:
    t = ap.get_encoder_motor_speed(1)
    if t is not None:
        vel = t
    t = ap.get_encoder_motor_speed(2)
    if t is not None:
        vel += t
    sleep(0.1)
print("Terminó el mov.")

print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
