from Crypto import Random
from Crypto.Cipher import AES


def generate_key():
  return Random.new().read(32)


def aes_cbc_encrypt(raw, key):
  iv = Random.new().read(AES.block_size)
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return {
    'iv': iv,
    'result': cipher.encrypt(pkcs7_pad(raw, AES.block_size))
  }


def aes_cbc_decrypt(enc, iv, key):
  cipher = AES.new(key, AES.MODE_CBC, iv)
  return pkcs7_unpad(cipher.decrypt(enc), AES.block_size)


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
