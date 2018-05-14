import time
import struct


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


class Frame:
    FRAME_TYPE_BYTE = 0x01
    FRAME_TYPE_FLOAT = 0x02
    FRAME_TYPE_SHORT = 0x03
    FRAME_TYPE_STRING = 0x04
    FRAME_TYPE_DOUBLE = 0x05
    FRAME_TYPE_LONG = 0x06
    FRAME_TYPE_ACK = 0xF0
    FRAME_TYPE_VERSION = 0xF1
    FRAME_TYPE_UNKNOWN = 0xFF

    def __init__(self, timestamp, frame_type, frame_data, frame_value):
        """

        :param timestamp:
        :param frame_type:
        :param frame_data: Raw frame data
        :param frame_value: Return value inside de frame (if exist)
        """
        self.timestamp = timestamp
        self.frame_type = frame_type
        self.frame_data = frame_data
        self.frame_value = frame_value

    def __str__(self):
        print '[{}]'.format(', '.join(hex(x) for x in self.frame_data))

    @staticmethod
    def is_frame(data):
        if len(data) >= 4:
            # Verifico el fin de la trama
            if data[-2:] == [0x0d, 0x0a]:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def generate_from_data(data):

        f_value = None
        f_type = None
        f_data = data
        f_timestamp = time.time()

        if data[0:2] == [0xff, 0x55]:
            if data[2:4] == [0x00, 0x01]:  # Byte
                f_type = Frame.FRAME_TYPE_BYTE
                f_value = data[4:]
            elif data[2:4] == [0x00, 0x02]:  # 2Byte Float
                f_type = Frame.FRAME_TYPE_FLOAT
                f_value = bytes2double(data[4:8])
                if f_value < -512 or f_value > 1023:
                    f_value = 0
            elif data[2:4] == [0x00, 0x03]:  # Short
                f_type = Frame.FRAME_TYPE_SHORT
                f_value = bytes2short(data[4:8])
            elif data[2:4] == [0x00, 0x04]:  # String
                s = ''.join([chr(s) for s in data[4:]])
                f_type = Frame.FRAME_TYPE_STRING
                f_value = s
            elif data[2:4] == [0x00, 0x05]:  # Double
                f_type = Frame.FRAME_TYPE_DOUBLE
                f_value = bytes2double(data[4:8])
            elif data[2:4] == [0x00, 0x06]:  # Long
                f_type = Frame.FRAME_TYPE_LONG
                f_value = bytes2long(data[4:8])
            elif data == [0xff, 0x55, 0x0d, 0x0a]:
                f_type = Frame.FRAME_TYPE_ACK
        else:
            if data[0:4] == [0x56, 0x65, 0x72, 0x73]:
                f_type = Frame.FRAME_TYPE_VERSION
                s = ''.join([chr(s) for s in data])
                f_value = s
            else:
                assert False, "generate_from_data: provided data is not a frame"

        return Frame(timestamp=f_timestamp, frame_type=f_type, frame_data=f_data, frame_value=f_value)
