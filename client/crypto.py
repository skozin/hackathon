import hmac
import hashlib

from Crypto import Random
from Crypto.Cipher import AES


def generate_key():
  return Random.new().read(32)


def encrypt(raw, key):
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(key, AES.MODE_CBC, iv)
  data = cipher.encrypt(pkcs7_pad(raw, AES.block_size))
  hmac = hmac_sha256_sign(key, data + iv)
  return {
    'data': data,
    'hmac': hmac,
    'iv': iv,
  }


def decrypt(data, iv, hmac, key):
  expected_hmac = hmac_sha256_sign(key, data + iv)
  if hmac != expected_hmac:
      raise ValueError('HMAC verification failed')
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return pkcs7_unpad(cipher.decrypt(data), AES.block_size)


def hmac_sha256_sign(message, key):
  return hmac.new(key, msg=message, digestmod=hashlib.sha256).digest()


def pkcs7_pad(data, block_size_bytes):
  """
  Pad an input data according to PKCS#7
  """
  l = len(data)
  val = block_size_bytes - (l % block_size_bytes)
  return data + bytearray([val] * val)


def pkcs7_unpad(data, block_size_bytes):
  """
  Remove the PKCS#7 padding from a text data.
  """
  val = data[-1]
  if val > block_size_bytes:
      raise ValueError('Input is not padded or padding is corrupt')
  l = len(data) - val
  return data[:l]
