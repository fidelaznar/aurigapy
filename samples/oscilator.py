from aurigapy import *
from time import sleep, time
from time import gmtime, strftime


def print_ts(s):
    ts = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print("%r| %r" % (ts, s))


def osc_velocity(step, osc_freq_steps, lin_vel, rot_vel_factor):
    t = (step % osc_freq_steps) / (osc_freq_steps*1.0)
    d = rot_vel_factor
    if t >= 0.5:
        speed_l = lin_vel + lin_vel * d
        speed_r = lin_vel - lin_vel * d
        move_pos = (t - 0.5) * 2
        move_dir = 1
    else:
        speed_l = lin_vel - lin_vel * d
        speed_r = lin_vel + lin_vel * d
        move_pos = t * 2
        move_dir = 0

    return speed_l, speed_r, move_pos, move_dir


ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(bluetooth)
print("Conectado")
sleep(3)
start = time()

i = 0

#Asi obtengo una frecuencia de unas 11 iteraciones por segundo, casi los 100ms estimados
while time() - start < 15:
    (sl, sr, pos, direction) = osc_velocity(step=i,
                                            osc_freq_steps=60,
                                            lin_vel=30,
                                            rot_vel_factor=0.4)

    ap.set_encoder_motor_rotate(1, -sr)
    ap.set_encoder_motor_rotate(2, sl)
    #sleep(0.1)

    i += 1
    print_ts("i=%r, sl=%r, sr=%r" % (i, sl, sr))

ap.reset_robot()
ap.close()
