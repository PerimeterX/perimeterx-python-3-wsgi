from enum import Enum


class PassReason(Enum):
    COOKIE = 'cookie'
    S2S = 's2s'
    S2S_TIMEOUT = 's2s_timeout'
    S2S_ERROR = 's2s_error'
    ENFORCER_ERROR = 'enforcer_error'

    def __str__(self):
        return str(self.value)
