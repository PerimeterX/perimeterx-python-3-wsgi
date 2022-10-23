from enum import Enum


class S2SErrorReason(Enum):
    NO_ERROR = ''
    BAD_REQUEST = 'bad_request'
    SERVER_ERROR = 'server_error'
    INVALID_RESPONSE = 'invalid_response'
    REQUEST_FAILED_ON_SERVER = 'request_failed_on_server'
    UNKNOWN_ERROR = 'unknown_error'

    def __str__(self):
        return str(self.value)
