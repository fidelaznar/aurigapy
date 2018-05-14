# coding=utf-8
from aurigapy import *
from time import *
from time import gmtime, strftime

ap = AurigaPy()

bluetooth = "/dev/tty.Makeblock-ELETSPP"
usb = "/dev/tty.wchusbserial1410"


def timestamp():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


def on_encoder_speed_readed(speed):
    print("%r E> %r" % (timestamp(), speed))


def on_forward(status):
    print("%r F> %r" % (timestamp(), status))


ap.connect(usb)  # on_connect
print("%r Conectado" % timestamp())


ap.set_command_until(command="forward", degrees=5000, speed=200, callback=on_forward)

# Despues del comando anterior hay que esperar 3 segundos para que la placa acabe...
# Esto no se necesita si se coje la versión sin callback
sleep(3)
print("%r End Sleep" % timestamp())

print("%r set_command start blocking" % timestamp())
ap.set_command_until(command="forward", degrees=-10000, speed=200)
print("%r set_command finish blocking" % timestamp())

for i in range(10):
    ap.get_encoder_motor_speed(1, on_encoder_speed_readed)
    sleep(1)


ap.set_encoder_motor_rotate(1, 1800, 200)
sleep(0.5)
print(ap.get_encoder_motor_speed(1))
sleep(1)

print("Closing...")

ap.reset_robot()
print("Reset robot...")
ap.close()
