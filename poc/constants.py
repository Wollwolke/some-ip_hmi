from enum import IntEnum


# Constants
class HeatedSeatLevel(IntEnum):
    OFF = 0
    MID = 1
    HIGH = 2

HMI_ADDRESS = '127.0.0.1'
HMI_PORT = 5668

SERVICE_IDS = {"REQ_USER_INPUT": 0x0001}

METHOD_IDS = {"NAV_ADDRESS": 0x0011, "HEATED_SEATS": 0x0021, "AC_TEMP": 0x0031}
