key = b"<RC4_KEY>"  # 替换为题目给定的密钥（字节）
cipher = bytes.fromhex("<CIPHER_HEX>")  # 从二进制数据段提取的 RC4 密文（十六进制）

S = list(range(256))
j = 0
for i in range(256):
    j = (j + S[i] + key[i % 8]) % 256
    S[i], S[j] = S[j], S[i]

i = j = 0
result = []
for b in cipher:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    result.append(b ^ S[(S[i] + S[j]) % 256])

print(bytes(result).decode())
