# coding=utf-8
import time
import threading


class Response:
    def __init__(self, timestamp, timeout, response_type, response_callback, response_event=None):
        self.timestamp = timestamp
        self.timeout = timeout
        self.response_type = response_type
        self.response_callback = response_callback
        self.response_event = response_event
        self.response_event_data = None

    @staticmethod
    def generate_response_async(callback, response_type, timeout=0.3):
        """

        :param callback: función con 2 parámetros (valor_respuesta, timeout). Timeout es true si se ha llamado
        por timeout y no por respuesta
        :param response_type:
        :param timeout:
        :return:
        """
        return Response(time.time(), timeout, response_type, callback, None)

    @staticmethod
    def generate_response_block(response_type, timeout=0.3):
        return Response(time.time(), timeout, response_type, None, threading.Event())

    def is_timeout(self):
        t_max = self.timestamp + self.timeout
        # print(self.timestamp, self.timeout, t_max,time.time())

        if t_max < time.time():
            return True
        else:
            return False

    def wait_blocking(self):
        assert self.response_event is not None, "Error, response is not blocking"
        self.response_event.wait()
