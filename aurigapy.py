# coding=utf-8

import glob
import struct
import sys
from time import sleep
import threading

import serial

STATUS_ACK = [0xff, 0x55, 0x0d, 0x0a]


def float2bytes(fval):
    """
    From <https://github.com/Kreativadelar>
    """
    val = struct.pack("f", fval)
    return [ord(val[0]), ord(val[1]), ord(val[2]), ord(val[3])]


def long2bytes(lval):
    """
    From <https://github.com/Kreativadelar>
    """
    val = struct.pack("=l", lval)
    return [ord(val[0]), ord(val[1]), ord(val[2]), ord(val[3])]


def bytes2long(data):
    return struct.unpack('<l', struct.pack('4B', *data))[0]


def bytes2double(data):
    return struct.unpack('<f', struct.pack('4B', *data))[0]


def bytes2short(data):
    return struct.unpack('<h', struct.pack('2B', *data))[0]


def short2bytes(sval):
    """
    From <https://github.com/Kreativadelar>
    """
    val = struct.pack("h", sval)
    return [ord(val[0]), ord(val[1])]


def char2byte(cval):
    """
    From <https://github.com/Kreativadelar>
    """
    val = struct.pack("b", cval)
    return ord(val[0])


class SerialCom:
    """
    From <https://github.com/Kreativadelar>
    """

    def __init__(self):
        self._serial = None

    def connect(self, port='/dev/tty.Makeblock-ELETSPP'):
        try:
            self._serial = serial.Serial(port, 115200, timeout=4)
        except:
            assert False, "Error: cannot open this port: " + port

    def device(self):
        return self._serial

    @staticmethod
    def scan_serial_ports():
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')
        result = []
        for port in ports:
            s = serial.Serial()
            s.port = port
            s.close()
            result.append(port)
        return result

    def write(self, data):
        self._serial.write(data)

    def read(self):
        return self._serial.read()

    def is_open(self):
        return self._serial.isOpen()

    def in_waiting(self):
        return self._serial.inWaiting()

    def close(self):
        self._serial.close()


class AurigaPy:
    def __init__(self, debug=False):

        self._serial = SerialCom()
        self.th = None
        self.exiting = False
        self._read_buffer = []
        self._callback = []
        self._on_callback = None
        self._on_callback_data = None
        self.debug = debug

    def _set_default_callback(self, data):
        self._on_callback_data = data
        self._on_callback.set()

    def _prepare_callback(self, callback):
        # Si no hay callback espero a recibir la respuesta
        if callback is None:
            self._on_callback = threading.Event()
            self._callback.append(self._set_default_callback)

    def _process_callback(self, callback, sleep_time=0):
        # Si no hay callback espero a que este libere la ejecucion
        if callback is None:
            if self.debug:
                print("Waiting to callback")
            self._on_callback.wait()
            #self._on_callback = None

            # Si no hay callback me espero el tiempo indicado a devolver el control
            # para que la placa haya terminado de ejecutar el comando
            sleep(sleep_time)

            return self._on_callback_data
        # Sino lo anyado a la lista de callbacks a procesar
        else:
            # TODO: Avisar que aqui no se espera el tiempo, lo debe gestionar quien lo implemente
            self._callback.append(callback)
            return None

    def _process_callback_nonblocking(self, callback, sleep_time=0):
        # Si no hay callback espero a que este libere la ejecucion
        if callback is None:
            #self._on_callback.wait()
            #self._on_callback = None

            # Si no hay callback me espero el tiempo indicado a devolver el control
            # para que la placa haya terminado de ejecutar el comando
            sleep(sleep_time)

            return self._on_callback_data
        # Sino lo anyado a la lista de callbacks a procesar
        else:
            # TODO: Avisar que aqui no se espera el tiempo, lo debe gestionar quien lo implemente
            self._callback.append(callback)
            return None

    def connect(self, port, callback=None):
        self._serial.connect(port)

        self._prepare_callback(callback)
        self.th = threading.Thread(target=self._data_reader, args=())
        self.th.start()

        self._process_callback(callback, sleep_time=2)

    #No bloquea esperando respuesta de la placa (en bluetooth no responde)
    def connect_wait_no_response(self, port, callback=None):
        self._serial.connect(port)

        self._prepare_callback(callback)
        self.th = threading.Thread(target=self._data_reader, args=())
        self.th.start()

    def _is_pkg(self, data):
        if len(data) >= 4:
            # Verifico el fin de la trama
            if data[-2:] == [0x0d, 0x0a]:
                return True
            else:
                return False

        else:
            return False

    def _process_pkg(self, data):
        if len(self._callback) > 0:
            cb = self._callback.pop(0)
            if cb is not None:
                if data[0:4] == [0xff, 0x55, 0x00, 0x01]:  # Byte
                    cb(data[4:])
                elif data[0:4] == [0xff, 0x55, 0x00, 0x02]:  # 2Byte Float
                    value = bytes2double(data[4:8])
                    if value < -512 or value > 1023:
                        value = 0
                    cb(value)
                elif data[0:4] == [0xff, 0x55, 0x00, 0x03]:  # Short
                    cb(bytes2short(data[4:8]))
                elif data[0:4] == [0xff, 0x55, 0x00, 0x04]:  # String
                    s = ''.join([chr(s) for s in data[4:]])
                    cb(s)
                elif data[0:4] == [0xff, 0x55, 0x00, 0x05]:  # Double
                    cb(bytes2double(data[4:8]))
                elif data[0:4] == [0xff, 0x55, 0x00, 0x06]:  # Long
                    cb(bytes2long(data[4:8]))
                elif data[0:4] == STATUS_ACK:
                    cb("ACK")
                elif data[0:8] == [0x56, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x3a]:
                    # Trama de inicio de conexión (str)
                    s = ''.join([chr(s) for s in data])
                    cb(s)
                # No se lo que es, lo paso a string
                else:
                    print("Warning: Unknown msg received")
                    s = ''.join([chr(s) for s in data])
                    cb(s)
            else:
                # Se recibió un paquete pero no hay callback registrado para procesarlo
                assert True, "Error, unexpected data received %r" % data
        else:
            print 'Ignoring [{}]'.format(', '.join(hex(x) for x in data))

    def _data_reader(self):
        while True:
            if self.exiting is True:
                break
            try:
                if self._serial.is_open() == True:
                    n = self._serial.in_waiting()
                    for i in range(n):
                        r = ord(self._serial.read())
                        self._read_buffer.append(r)
                    sleep(0.01)

                    # Si existe un paquete lo proceso y borro el bufer de lectura
                    if self._is_pkg(self._read_buffer):
                        if self.debug:
                            print 'Processing [{}]'.format(', '.join(hex(x) for x in self._read_buffer))
                        self._process_pkg(list(self._read_buffer))
                        self._read_buffer = []

                else:
                    sleep(0.5)
            except Exception, ex:
                print str(ex)
                sleep(1)

    def _write(self, data):
        if self.debug:
            print 'Writing [{}]'.format(', '.join(hex(x) for x in data))
        self._serial.write(data)

    def reset_robot(self):
        self._prepare_callback(None)
        self._serial.write(bytearray([0xff, 0x55, 0x2, 0x0, 0x4]))
        self._read_buffer = []

    # ff 55 09 00 02 08 00 02
    # Led 0 son todos
    def set_led_onboard(self, led, r, g, b, callback=None):
        assert led >= 0 and led < 12, "Error, led fuera de rango"
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 0x09, 0x00, 0x02, 0x08, 0x00, 0x02,
                          led, r, g, b])
        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        self._process_callback_nonblocking(callback)

    # ff 55 0b 00 02 3e 01 <slot> <long4 degrees> 0 0 <short2 vel>
    def set_encoder_motor_rotate(self, slot, degrees, speed, callback=None):
        assert slot == 1 or slot == 2, "Error, slot not defined"
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 0x0b, 0x00, 0x02, 0x3e, 0x01, slot] +
                         long2bytes(degrees) +
                         short2bytes(speed))
        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        self._process_callback(callback, sleep_time=0.1)

    def set_command_until(self, command, degrees, speed, callback=None):
        # ff 55 0b 00 02 3e 05 <cmd> <4long degrees> <2short speed>
        commands = ["forward", "backward", "left", "right"]
        assert command in commands, "Error, %r command not in %r" % (command, str(commands))
        ind = 1 + commands.index(command)

        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 0x0b, 0x00, 0x02, 0x3e, 0x05, ind] +
                         long2bytes(degrees) +
                         short2bytes(speed))

        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        self._process_callback(callback, sleep_time=0.1)

    def set_command(self, command, speed, callback=None):
        # ff 55 07 00 02 05 <2short speedleft> <2short speedright>
        commands = ["forward", "backward", "right", "left"]
        assert command in commands, "Error, %r command not in %r" % (command, str(commands))

        if command == "forward":
            speed_left = -speed
            speed_right = speed
        elif command == "backward":
            speed_left = speed
            speed_right = -speed
        elif command == "left":
            speed_left = -speed
            speed_right = -speed
        elif command == "right":
            speed_left = speed
            speed_right = speed
        else:
            assert True, "Error in set_command"

        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 0x07, 0x00, 0x02, 0x5] +
                         short2bytes(speed_left) +
                         short2bytes(speed_right))

        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        self._process_callback(callback, sleep_time=0)

    # ff 55 06 00 01 3d 00 <slot> 02
    def get_encoder_motor_speed(self, slot, callback=None):
        assert slot == 1 or slot == 2, "Error, slot not defined"
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 6, 0, 1, 0x3d, 0, slot, 2])
        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        return self._process_callback(callback, sleep_time=0.1)

    # ff 55 06 00 01 3d 00 <slot> 01
    def get_encoder_motor_degrees(self, slot, callback=None):
        assert slot == 1 or slot == 2, "Error, slot not defined"
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 6, 0, 1, 0x3d, 0, slot, 1])
        # print '[{}]'.format(', '.join(hex(x) for x in data))
        self._write(data)
        return self._process_callback(callback, sleep_time=0.1)

    # ff 55 04 00 01 01 <port>
    def get_ultrasonic_reading(self, port, callback=None):
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 4, 0, 1, 1, port])
        self._write(data)
        return self._process_callback(callback)

    # ff 55 04 00 01 03 <port>
    def get_light_sensor(self, port, callback=None):
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 4, 0, 1, 3, port])
        self._write(data)
        return self._process_callback(callback)

    def get_light_sensor_onboard(self, port, callback=None):
        assert port == 1 or port == 2, "Error, port not defined"
        port = 0x0c if port == 1 else 0x0b
        return self.get_light_sensor(port, callback)

    # ff 55 04 00 01 07 <port>
    def get_sound_sensor(self, port, callback=None):
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 4, 0, 1, 7, port])
        self._write(data)
        return self._process_callback(callback)

    def get_sound_sensor_onboard(self, callback=None):
        port = 0x0e
        return self.get_light_sensor(port, callback)

    # ff 55 04 00 01 1b 0d
    def get_temperature_sensor_onboard(self, callback=None):
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 4, 0, 1, 0x1b, 0x0d])
        self._write(data)
        return self._process_callback(callback)

    # ff 55 04 00 01 11 <port>
    def get_line_sensor(self, port, callback=None):
        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 4, 0, 1, 0x11, port])
        self._write(data)
        return self._process_callback(callback)

    # ff 55 05 00 01 06 01 <axis>
    def get_gyro_sensor_onboard(self, axis, callback=None):
        axis_opt = ["x", "y", "z"]
        assert axis in axis_opt, "Error, axis %r not defined in %r" % (axis, axis_opt)
        axis_ind = 1 + axis_opt.index(axis)

        self._prepare_callback(callback)
        data = bytearray([0xff, 0x55, 5, 0, 1, 6, 1, axis_ind])
        self._write(data)
        return self._process_callback(callback)

    def close(self):

        print("Waiting 2 seconds to kill reader thread...")

        sleep(2)
        self.exiting = True

    def __del__(self):
        self.exiting = True
        self._serial.close()
