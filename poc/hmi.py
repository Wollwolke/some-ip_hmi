#! /usr/bin/env/python3
from scapy.all import StreamSocket
from eth_scapy_someip import eth_scapy_someip as someip
import time
import socket
import constants as const


class HMIController:
    def __init__(self) -> None:
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(("0.0.0.0", const.HMI_PORT))
        self.stream_socket = None

    def __del__(self):
        self.server_socket.close()

    def startup(self):
        try:
            while True:
                self.listen()
        except KeyboardInterrupt:
            pass

    def process_msg(self, sip):
        if sip.msg_id.srv_id != const.SERVICE_IDS["REQ_USER_INPUT"]:
            self.send_error(sip, sip.RET_E_UNKNOWN_SERVICE)
            return

        if sip.msg_id.method_id == const.METHOD_IDS.get("NAV_ADDRESS"):
            print("Got 'NAV_ADDRESS' request")
            time.sleep(3)
            self.send_response(sip, "Wolkenstraße 77")
        elif sip.msg_id.method_id == const.METHOD_IDS.get("HEATED_SEATS"):
            print("Got 'HEATED_SEATS' request")
            time.sleep(1)
            self.send_response(
                sip, const.HeatedSeatLevel.MID.to_bytes(1, byteorder="big")
            )
        elif sip.msg_id.method_id == const.METHOD_IDS.get("AC_TEMP"):
            print("Got 'AC_TEMP' request")
            time.sleep(2)
            self.send_response(sip, (22).to_bytes(4, byteorder="big"))
        else:
            self.send_error(sip.RET_E_UNKNOWN_METHOD)
        print("Sent response")
        print("-" * 40)

    def listen(self):
        self.server_socket.listen(1)
        print("Waiting for client")
        conn, _ = self.server_socket.accept()
        self.stream_socket = StreamSocket(conn)
        msg = self.stream_socket.recv(4096)
        self.process_msg(someip.SOMEIP(msg.load))

    def send_error(self, request, reason):
        response = someip.SOMEIP()

        response.msg_id = request.msg_id
        response.req_id = request.req_id
        response.msg_type = response.TYPE_ERROR
        response.retcode = reason

        self.stream_socket.send(response)

    def send_response(self, request, payload):
        response = someip.SOMEIP()

        response.msg_id = request.msg_id
        response.req_id = request.req_id
        response.msg_type = response.TYPE_RESPONSE
        response.retcode = response.RET_E_OK
        response.add_payload(payload)

        self.stream_socket.send(response)


if __name__ == "__main__":
    hmi = HMIController()
    hmi.startup()
