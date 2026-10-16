# -*- coding: utf-8 -*-
# simpleBase64 自定义 Base64 换表解密脚本
# 原理：题目用了一张自定义 Base64 表（大小写字母各 ROT13 偏移，数字和 +/ 不变）。
#       把密文中每个字符按"自定义表中的位置"映射回"标准表同位置字符"，
#       再做标准 Base64 解码即可。

import base64

custom = 'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/'
std    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
ct = 'DIqUD1ETr3AcGKNkZ19PLKAyAwEsAIELHx1nFSH2IwyGsD=='

ct_clean = ct.rstrip('=')
mapped = ''.join(std[custom.index(c)] for c in ct_clean)
mapped += '=' * (len(ct) - len(ct_clean))

flag = base64.b64decode(mapped).decode()
print("flag =", flag)
