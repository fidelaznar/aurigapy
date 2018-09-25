# coding=utf-8
from aurigapy.aurigapy import *
from time import *
import numpy as np

ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def rot_degrees(angle):
    return round(1003 / 360.0 * angle)


print("%r Conectando..." % timestamp())
ap.connect(bluetooth)
print("%r Conectado!" % timestamp())

sleep(2)


def ultrasonic_read():
    tr = 0
    times = 3
    for i in range(times):
        r = ap.get_ultrasonic_reading(8)
        if r is not None:
            tr += r

    return tr / times


def perceive(per_angle):
    readings = []

    sleep(0.3)

    ap.set_led_onboard(0, 0, 0, 50)
    readings.append(ultrasonic_read())

    ap.set_led_onboard(0, 0, 50, 50)
    ap.move_to(command="right", degrees=rot_degrees(per_angle), speed=125)
    readings.append(ultrasonic_read())

    ap.set_led_onboard(0, 50, 50, 0)
    ap.move_to(command="left", degrees=rot_degrees(2 * per_angle), speed=255)
    readings.append(ultrasonic_read())

    ap.move_to(command="right", degrees=rot_degrees(per_angle), speed=125)
    ap.set_led_onboard(0, 50, 50, 50)

    return readings


def rotate_dir(dir, per_angle):
    if dir == 1:
        ap.move_to(command="right", degrees=rot_degrees(per_angle), speed=255)
    elif dir == 2:
        ap.move_to(command="left", degrees=rot_degrees(per_angle), speed=255)
    elif dir == 3:
        ap.move_to(command="backward", degrees=2 * 191, speed=125)
        ap.move_to(command="left", degrees=rot_degrees(90), speed=255)


per_angle = 50
start = time()

while time() - start < 120:
    readings = np.asarray(perceive(per_angle))

    readings_no_400 = readings[readings != 400]

    if len(readings_no_400) > 0 and np.max(readings_no_400) < 100:
        best_dir = 3
    else:
        best_dir = np.argmax(readings)

    ap.set_led_onboard(0, 50, 0, 50)
    print(best_dir, readings)
    rotate_dir(best_dir, per_angle)

    ap.set_led_onboard(0, 50, 0, 0)
    # Muevo como máximo 30 cm adelante
    ap.move_to(command="forward", degrees=min(np.max(readings)*9, 192 * 3), speed=125)

print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
