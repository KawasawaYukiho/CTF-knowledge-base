# -*- coding: utf-8 -*-
"""
Docker 镜像历史与文件恢复解题脚本
cipher.txt 是 OpenSSL “Salted__” 格式的加盐 AES：
  base64 解码后前 8 字节为 Salted__，其后 8 字节是 salt，再后是密文。
本题口令由两处隐写给出：
  - avatar.png 尾部拼了一段 WAV，Audacity 看频谱得到 secret.zip 的解压口令；
  - note.txt 诗句“爱憎可分明”给出 AES 口令。
用 PBKDF2(SHA256) 派生密钥，AES-256-CBC / PKCS7 解密。
依赖：pip install pycryptodome
"""
import base64
import hashlib
import sys

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad


def openssl_evp_decrypt(b64, password):
    raw = base64.b64decode(b64)
    assert raw[:8] == b"Salted__", "不是 OpenSSL Salted__ 格式"
    salt = raw[8:16]
    ct = raw[16:]
    # EVP_BytesToKey 的 PBKDF2 等价参数（本题在线工具用 PBKDF2+SHA256）
    key_iv = PBKDF2(password, salt, dkLen=48, count=1,
                    hmac_hash_module=hashlib.sha256)
    key, iv = key_iv[:32], key_iv[32:48]
    pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), AES.block_size)
    return pt


if __name__ == "__main__":
    b64 = open("cipher.txt", encoding="utf-8").read().strip()
    # AES 口令来自 note.txt 诗句提示（中间线索，非 flag 本身）
    aes_password = sys.argv[1] if len(sys.argv) > 1 else "REPLACE_WITH_NOTE_PASSWORD"
    try:
        pt = openssl_evp_decrypt(b64, aes_password)
        print("[*] 解密成功，明文为 flag：", pt)
    except Exception as e:
        print("[-] 解密失败，请确认 AES 口令：", e)
