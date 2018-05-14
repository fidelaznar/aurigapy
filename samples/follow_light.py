from aurigapy import *
from time import sleep, time
from time import gmtime, strftime


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())

ap = AurigaPy(debug=False)

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1420"

ap.connect(bluetooth)
print("Conectado")

sleep(3)
start = time()

while time() - start < 120:
    l1 = ap.get_light_sensor_onboard(1)
    l2 = ap.get_light_sensor_onboard(2)
    sleep(0.2)

    v = 80.0 * ((l1 + l2) / 2000.0)
    iv = int(v)

    if v > 30:
        if l1 > l2:
            print(">")
            ap.set_encoder_motor_rotate(1, -iv)
            ap.set_encoder_motor_rotate(2, 0)
        else:
            print("<")
            ap.set_encoder_motor_rotate(1, 0)
            ap.set_encoder_motor_rotate(2, iv)
    else:
        ap.set_encoder_motor_rotate(1, 0)
        ap.set_encoder_motor_rotate(2, 0)

    sleep(0.1)

ap.reset_robot()
ap.close()
