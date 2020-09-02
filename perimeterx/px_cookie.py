import base64
import binascii
import hashlib
import json
import struct
import sys
import traceback
import hashlib
from time import time

from Crypto.Cipher import AES

from perimeterx import px_enc_utils
from perimeterx.px_constants import *


class PxCookie(object):

    def __init__(self, config):
        self._config = config
        self._logger = config.logger
        self._raw_cookie = ''
        self._hmac = ''

    def build_px_cookie(self, px_cookies, user_agent=''):
        self._logger.debug("PxCookie[build_px_cookie]")
        if not px_cookies:
            self._logger.debug('Cookie is missing')
            return None

        px_cookie_keys = px_cookies.keys()
        sorted(px_cookie_keys, reverse=True)
        for prefix in px_cookie_keys:
            if prefix == PREFIX_PX_TOKEN_V1 or prefix == PREFIX_PX_COOKIE_V1:
                self._logger.debug('Cookie/Token V1 found, evaluating..')
                from perimeterx.px_cookie_v1 import PxCookieV1
                return prefix, PxCookieV1(self._config, px_cookies[prefix])
            if prefix == PREFIX_PX_TOKEN_V3 or prefix == PREFIX_PX_COOKIE_V3:
                self._logger.debug('Cookie/Token V3 found, evaluating..')
                from perimeterx.px_cookie_v3 import PxCookieV3
                ua = ''
                if prefix == PREFIX_PX_COOKIE_V3:
                    ua = user_agent
                return prefix, PxCookieV3(self._config, px_cookies[prefix], ua)

        self._logger.debug('Cookie is missing')

    def decode_cookie(self):
        self._logger.debug("PxCookie[decode_cookie]")
        return px_enc_utils.decode_cookie(self._config, self._raw_cookie)

    def decrypt_cookie(self):
        """
        Decrypting the PerimeterX risk cookie using AES
        :return: Returns decrypted value if valid and False if not
        :rtype: Bool|String
        """
        try:
            parts = self._raw_cookie.split(':', 3)
            if len(parts) != 3:
                return False
            salt = base64.b64decode(parts[0])
            iterations = int(parts[1])
            if iterations < 1 or iterations > 10000:
                return False
            data = base64.b64decode(parts[2])
            dk = hashlib.pbkdf2_hmac(hash_name='sha256', password=self._config.cookie_key.encode(), salt=salt, iterations=iterations, dklen=48)
            key = dk[:32]
            iv = dk[32:]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            unpad = lambda s: s[0:-s[-1]]
            plaintext = unpad(cipher.decrypt(data))
            self._logger.debug('cookie decrypted')
            return plaintext
        except:
            print (traceback.format_exception(*sys.exc_info()))
            return None

    def is_cookie_expired(self):
        """
        Checks if cookie validity time expired.
        :return: Returns True if valid and False if not
        :rtype: Bool
        """
        now = int(round(time() * 1000))
        expire = self.get_timestamp()
        return now > expire

    def is_cookie_valid(self, str_to_hmac):
        """
        Checks if cookie hmac signing match the request.
        :return: Returns True if valid and False if not
        :rtype: Bool
        """
        try:
            calculated_digest = px_enc_utils.create_hmac(str_to_hmac, self._config)
            return self.get_hmac() == calculated_digest
        except Exception as err:
            self._logger.debug("failed to calculate hmac: {}".format(err))
            return False

    def deserialize(self):
        logger = self._logger
        if self._config.encryption_enabled:
            cookie = px_enc_utils.decrypt_cookie(config=self._config, raw_cookie=self._raw_cookie)
        else:
            cookie = px_enc_utils.decode_cookie(config=self._config, raw_cookie=self._raw_cookie)

        if not cookie:
            return False

        logger.debug('Original token deserialized: {}'.format(cookie))
        self.decoded_cookie = json.loads(cookie)
        return self.is_cookie_format_valid()

    def is_high_score(self):
        return self.get_score() >= self._config.blocking_score

    def get_timestamp(self):
        return self.decoded_cookie['t']

    def get_uuid(self):
        return self.decoded_cookie['u']

    def get_vid(self):
        return self.decoded_cookie['v']

    def get_age(self):
        return int(round(time() * 1000)) - self.decoded_cookie['t']

    def get_hmac(self):
        return self._hmac
