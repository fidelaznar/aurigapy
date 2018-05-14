# coding=utf-8
from aurigapy import *
from time import *
from time import gmtime, strftime

ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1410"


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


print("%r Conectando..." % timestamp())
ap.connect_wait_no_response(bluetooth)
sleep(3)
print("%r Conectado!" % timestamp())

# speed [0,255]
print(ap.get_encoder_motor_degrees(1))
ap.set_command_until(command="right", degrees=460, speed=125)

sleep(0.25)

# Espero a que termine
vel = 1
while vel != 0:
    vel = ap.get_encoder_motor_speed(1)
    vel += ap.get_encoder_motor_speed(2)
    print(vel)
    sleep(0.1)

print(ap.get_encoder_motor_degrees(1))
ap.set_command_until(command="left", degrees=460, speed=125)

sleep(0.25)

# Espero a que termine
vel = 1
while vel != 0:
    vel = ap.get_encoder_motor_speed(1)
    vel += ap.get_encoder_motor_speed(2)
    print(vel)
    sleep(0.1)

print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
