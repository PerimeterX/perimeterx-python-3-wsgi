import hashlib
import hmac
import base64
from Crypto.Cipher import AES


def create_hmac(str_to_hmac, config):
    try:
        return hmac.new(config.cookie_key.encode(), str_to_hmac.encode(), hashlib.sha256).hexdigest()
    except Exception:
        config.logger.debug("Failed to calculate hmac")
        return False

def decrypt_cookie(config, raw_cookie):
    """
    Decrypting the PerimeterX risk cookie using AES
    :return: Returns decrypted value if valid and False if not
    :rtype: Bool|String
    """
    logger = config.logger
    logger.debug("PxCookie[decrypt_cookie]")
    try:
        parts = raw_cookie.split(':', 3)
        if len(parts) != 3:
            return False
        salt = base64.b64decode(parts[0])
        iterations = int(parts[1])
        if iterations < 1 or iterations > 10000:
            return False
        data = base64.b64decode(parts[2])
        dk = hashlib.pbkdf2_hmac(hash_name='sha256', password=config.cookie_key.encode(), salt=salt, iterations=iterations, dklen=48)
        key = dk[:32]
        iv = dk[32:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        unpad = lambda s: s[0:-s[-1]]
        plaintext = unpad(cipher.decrypt(data))
        logger.debug("PxCookie[decrypt_cookie] cookie decrypted")
        return plaintext
    except Exception as e:
        logger.error('Encryption tool encountered a problem during the decryption process: ' + str(e))
        return False


def decode_cookie(config, raw_cookie):
    config.logger.debug("PxCookie[decode_cookie]")
    return base64.b64decode(raw_cookie)
