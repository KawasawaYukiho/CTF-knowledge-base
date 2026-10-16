# -*- coding: utf-8 -*-
"""
TCP 流重组与 HTTP 还原解题脚本
思路：
  1. flow_1.pcap 里藏着一个 HTTP 请求头 X-password（base64），解出解压 zip 的密码。
  2. flow_2.pcap 里是另一条 TCP 流，里面拼着一个完整的 zip（PK 头开始）。
     纯 Python 遍历 pcap 数据包，把 TCP payload 按包序拼起来，再按 PK 特征切出 secret.zip。
  3. 用上面的密码解压 secret.zip 得到 hidden.png，再用 zsteg 扫 LSB 最低有效位隐写。
依赖：仅标准库（zsteg 步骤需另行安装 gem install zsteg）。
"""
import base64
import struct
import sys


def iter_pcap_payloads(path):
    """遍历 libpcap 文件，按数据包出现顺序吐出每一个包的 TCP 载荷字节。
    本题 pcap linktype=228(RAW)，即包体直接从 IP 头开始，无 14 字节以太网头。"""
    with open(path, "rb") as f:
        data = f.read()
    linktype = struct.unpack("<I", data[20:24])[0]
    l2 = 14 if linktype == 1 else 0      # 1=Ethernet 跳过14字节；RAW(228/101)不跳
    off = 24
    payloads = []
    while off + 16 <= len(data):
        incl_len = struct.unpack("<I", data[off + 8:off + 12])[0]
        off += 16
        pkt = data[off:off + incl_len]
        off += incl_len
        ip = pkt[l2:]
        if len(ip) < 20 or (ip[0] >> 4) != 4:
            continue
        ihl = (ip[0] & 0x0F) * 4
        if ip[9] != 6:                    # 只处理 TCP
            continue
        total_len = struct.unpack(">H", ip[2:4])[0]
        tcp = ip[ihl:total_len]
        doff = (tcp[12] >> 4) * 4
        payload = tcp[doff:]
        if payload:
            payloads.append(payload)
    return payloads


def find_x_password(payloads):
    for p in payloads:
        low = p.lower()
        if b"x-password" in low:
            for ln in p.split(b"\r\n"):
                if ln.lower().startswith(b"x-password"):
                    token = ln.split(b":", 1)[1].strip()
                    return base64.b64decode(token).decode()
    return None


def carve_zip(payloads):
    """把 TCP 载荷拼成原始字节流，从 PK\\x03\\x04 切到 EOCD(PK\\x05\\x06) 结束。"""
    stream = b"".join(payloads)
    start = stream.find(b"PK\x03\x04")
    if start < 0:
        return None
    end = stream.rfind(b"PK\x05\x06")
    if end < 0:
        return None
    # EOCD 记录本身 22 字节 + 注释长度，这里直接取到 EOCD 结尾附近
    eocd = stream[end:end + 22]
    comment_len = struct.unpack("<H", eocd[20:22])[0]
    return stream[start:end + 22 + comment_len]


def main():
    pwd = find_x_password(iter_pcap_payloads("flow_1.pcap"))
    print("[*] 从 flow_1 解出的 zip 解压密码：", pwd)

    blob = carve_zip(iter_pcap_payloads("flow_2.pcap"))
    if blob:
        with open("secret.zip", "wb") as f:
            f.write(blob)
        print("[*] 已从 flow_2 的 TCP 流拼出 secret.zip，字节数：", len(blob))
    else:
        print("[-] 未在 flow_2 中找到完整 zip，可在 Wireshark 右键 Follow -> TCP Stream 手动另存。")

    print("[*] 下一步：用上面密码解压 secret.zip 得 hidden.png，然后")
    print("    zsteg hidden.png   # 扫 LSB 各通道，结果即为 flag")


if __name__ == "__main__":
    main()
