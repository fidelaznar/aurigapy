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

start = time()

fps_timer = time()
fps_counter = 0

# Pruebas realizadas
# ___________________________________________________________
# ultrasonido + mov_encoder                     08 fps
# ultrasonido + giro (3 ejes) + mov_encoder     04 fps
# mov_encoder                                   12 fps, 0.083s
# ultrasonido                                   22 fps, 0.045s
# giro (3 ejes)                                 08 fps, 0.125s
# giro (1 eje)                                  25 fps, 0.04s

while time() - start < 20:

    if time() - fps_timer >= 1:
        fps_timer = time()
        print("fps (hz) : %r, freq (s): %r" % (fps_counter, 1.0/fps_counter))
        fps_counter = 0

    r = ap.get_ultrasonic_reading(10)
    r = ap.get_ultrasonic_reading(10)
    x = ap.get_gyro_sensor_onboard("x")
    y = ap.get_gyro_sensor_onboard("y")
    z = ap.get_gyro_sensor_onboard("z")

    ap.set_encoder_motor_rotate(1, 15)
    ap.set_encoder_motor_rotate(2, -15)

    fps_counter += 1

ap.reset_robot()
ap.close()
