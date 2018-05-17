# coding=utf-8
from aurigapy import *
from time import sleep, time
from time import gmtime, strftime
import numpy as np


def print_ts(s):
    ts = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("%r| %r" % (ts, s))


def osc_velocity(step, osc_freq_steps, lin_vel, rot_vel_factor):
    t = (step % osc_freq_steps) / (osc_freq_steps * 1.0)
    d = rot_vel_factor
    if t >= 0.5:
        set_light_rgb(5, 100, 0, 0)
        speed_l = lin_vel + lin_vel * d
        speed_r = lin_vel - lin_vel * d
        move_pos = (t - 0.5) * 2
        move_dir = 1
    else:
        set_light_rgb(5, 0, 0, 100)
        speed_l = lin_vel - lin_vel * d
        speed_r = lin_vel + lin_vel * d
        move_pos = t * 2
        move_dir = 0
    return speed_l, speed_r, move_pos, move_dir


def set_light(val):
    ap.set_led_onboard(1, r=val, g=val, b=val)


def set_light_rgb(led, r, g, b):
    ap.set_led_onboard(led, r=r, g=g, b=b)


def capture(num_readings, move_pos, move_direction):
    read_inc = (1.0 / num_readings) * capture.read_sec + 1.0 / num_readings / 2
    available_readings = None

    if move_pos >= read_inc:
        set_light(125)
        capture.part_sonar.append(ap.get_ultrasonic_reading(10))
        capture.read_sec += 1
    else:
        set_light(0)

    if capture.cur_dir != move_direction:

        if capture.cur_dir == 1:
            capture.part_sonar = list(reversed(capture.part_sonar))

        available_readings = capture.part_sonar

        capture.read_sec = 0
        capture.cur_dir = move_direction
        capture.part_sonar = []

    return available_readings


def avoider(readings, sl, sr, rotate_on_near):
    ron = rotate_on_near
    ai = np.argmin(np.asarray(readings))
    am = readings[ai]
    if ai == 0:
        sr = sr * .8 + (400 - am) * .1
        #print("SL: ", sl)
    elif ai == 2:
        sl = sl * .8 + (400 - am) * .1
        #print("SR: ", sr)
    else:
        print ai

    if readings[1] < 50:
        if ron is None:
            ron = np.argmax(np.asarray(readings))
        if ron == 0:
            sl = 0
            sr = -50
        else:
            sl = -50
            sr = 0
    else:
        ron = None

    return sl, sr, ron


# Variables estáticas de la función capture
capture.read_sec = 0
capture.cur_dir = 0
capture.part_sonar = []

ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(bluetooth)
print("Conectado")
sleep(3)

# Numero de lecturas por oscilacion
num_readings = 3
# Lecturas más actuales
readings = None
# Si estoy dentro de la distancia de seguridad
rotate_on_near = None

start = time()
i = 0
tr = None
# Asi obtengo una frecuencia de unas 11 iteraciones por segundo, casi los 100ms estimados
while time() - start < 60:
    (sl, sr, pos, direction) = osc_velocity(step=i,
                                            osc_freq_steps=60,
                                            lin_vel=20,
                                            rot_vel_factor=0.4)

    # Capturo las lecturas
    tr = capture(num_readings, pos, direction)

    if tr is not None:
        readings = tr
        print_ts("Readings: %r" % readings)

    if readings is not None:
        sl, sr, rotate_on_near = avoider(readings, sl, sr, rotate_on_near)
        ap.set_encoder_motor_rotate(1, -sr)
        ap.set_encoder_motor_rotate(2, sl)
        set_light_rgb(7, 0, 100, 0)
        sleep(2)
        set_light_rgb(7, 0, 0, 0)
        readings = None
    else:
        ap.set_encoder_motor_rotate(1, -sr)
        ap.set_encoder_motor_rotate(2, sl)

    i += 1

ap.reset_robot()
ap.close()
