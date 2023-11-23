#! /usr/bin/env/python3
from scapy.all import StreamSocket
from eth_scapy_someip import eth_scapy_someip as someip
import constants as const
import sys
import socket
import time
from random import uniform


class App:
    def __init__(self) -> None:
        self.session_id = 0

    def startup(self):
        try:
            while True:
                time.sleep(uniform(2.0, 5.0))
                while not self.send_request():
                    print("Retrying...")
                    time.sleep(1)
                self.session_id += 1
        except KeyboardInterrupt:
            pass

    def build_request(self, method_id):
        sip = someip.SOMEIP()

        sip.msg_id.srv_id = const.SERVICE_IDS["REQ_USER_INPUT"]
        sip.msg_id.sub_id = 0x0
        sip.msg_id.method_id = method_id

        sip.req_id.client_id = self.CLIENT_ID
        sip.req_id.session_id = self.session_id

        sip.msg_type = sip.TYPE_REQUEST
        sip.retcode = sip.RET_E_OK

        return sip

    def send_request(self, req):
        self.log(f"Send request with ID {self.session_id}")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((const.HMI_ADDRESS, const.HMI_PORT))
        except socket.error as e:
            self.log(f"Error connecting to HMI: {e}")
            return None
        stream_socket = StreamSocket(client_socket)
        response = stream_socket.sr1(req, verbose=0, timeout=6)
        client_socket.close()
        return response

    def log(self, msg):
        print(f"{self.__class__.__name__}: {msg}")

class NavApp(App):
    CLIENT_ID = 0xDEAD

    def build_request(self):
        return super().build_request(const.METHOD_IDS["NAV_ADDRESS"])

    def send_request(self):
        request = self.build_request()
        response = super().send_request(request)
        if None == response:
            return False

        response = someip.SOMEIP(response.load)
        if response.req_id == request.req_id and response.msg_id == request.msg_id:
            self.log(f"Response: {response.payload.original.decode('utf-8')}\n")
        else:
            self.log("Got invalid response")
            return False
        return True

class SeatsApp(App):
    CLIENT_ID = 0xABCD

    def build_request(self):
        return super().build_request(const.METHOD_IDS["HEATED_SEATS"])

    def send_request(self):
        request = self.build_request()
        response = super().send_request(request)
        if None == response:
            return False

        response = someip.SOMEIP(response.load)
        if response.req_id == request.req_id and response.msg_id == request.msg_id:
            self.log(f"Response: {const.HeatedSeatLevel(int.from_bytes(response.payload.original)).name}\n")
        else:
            self.log("Got invalid response")
            return False
        return True

class AcApp(App):
    CLIENT_ID = 0xBEEF

    def build_request(self):
        return super().build_request(const.METHOD_IDS["AC_TEMP"])

    def send_request(self):
        request = self.build_request()
        response = super().send_request(request)
        if None == response:
            return False

        response = someip.SOMEIP(response.load)
        if response.req_id == request.req_id and response.msg_id == request.msg_id:
            self.log(f"Response: {int.from_bytes(response.payload.original)}\n")
        else:
            self.log("Got invalid response")
            return False
        return True

def main():
    if len(sys.argv) != 2:
        print("Provide exactly one argument: Nav, Ac, Seats")
        return
    
    param = sys.argv[1]

    if param == "Nav":
        app = NavApp()
    elif param == "Ac":
        app = AcApp()
    elif param == "Seats":
        app = SeatsApp()
    else:
        print("Provide exactly one argument: Nav, Ac, Seats")
        return
    
    app.startup()


if __name__ == "__main__":
    main()
