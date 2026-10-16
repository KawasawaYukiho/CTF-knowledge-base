# -*- coding: utf-8 -*-
# hex & base 组合编码通用还原脚本
# 套路：一长串 Base64 连续解两次（解完还是 Base64）-> 得到空格分隔的十六进制字节 -> hex 转 ASCII。
# 本脚本为通用还原逻辑，使用时把密文替换进去即可。
import base64

def double_b64(s: str) -> bytes:
    d1 = base64.b64decode(s)      # 第一次 Base64 解码，结果通常仍是一段 Base64
    d2 = base64.b64decode(d1)     # 第二次 Base64 解码
    return d2

def hex_bytes_to_ascii(hex_str: str) -> str:
    # 输入形如 "66 6c 61 67 ..." 的空格分隔十六进制，两位一组转一个字节
    return bytes.fromhex(hex_str.replace(" ", "")).decode()

if __name__ == "__main__":
    # 用法（把密文替换进去）：
    # ciphertext = "<一长串 Base64>"
    # raw = double_b64(ciphertext)          # -> 得到一行十六进制
    # print(hex_bytes_to_ascii(raw.decode()))   # -> 得到 flag
    print("用法见脚本注释：double_b64 解两次，再 hex_bytes_to_ascii 转 ASCII")
