# -*- coding: utf-8 -*-
"""
docm 宏提取与 VBA 分析解题脚本
本题 flag 分两半：
  后半段：二维码里 32 行几乎相同的 base64，利用 base64 末字符低 2 bit 补位藏信息。
  前半段：VBA 宏吐出的超长 base64 -> 社会主义核心价值观编码 -> “南北绿豆”四进制。
          由已知前缀反推编码表：南=1, 北=0, 绿=3, 豆=2，每 4 符号拼 1 字节。
"""
import base64

B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def last_two_bit(line):
    """取一行 base64 的最后一个有效字符(去掉=填充)的 6bit 值的低 2bit。"""
    line = line.strip().rstrip("=")
    ch = line[-1]
    idx = B64.index(ch)
    return idx & 0b11  # 低 2 bit


def extract_tail_hidden(path):
    bits = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        bits.append(last_two_bit(ln))
    raw = 0
    n = 0
    out = []
    for b in bits:  # 每 8 bit 拼一个 ASCII 字符
        raw = (raw << 2) | b
        n += 2
        if n == 8:
            out.append(chr(raw))
            raw, n = 0, 0
    return "".join(out)


# 南北绿豆四进制：由已知前缀反推得到
BASE4 = {"南": 1, "北": 0, "绿": 3, "豆": 2}


def decode_base4(sequence):
    """sequence: 空格/换行分隔的“南北绿豆”串，每 4 个符号拼 1 字节 ASCII。"""
    chars = [c for c in sequence if c in BASE4]
    out = []
    for i in range(0, len(chars), 4):
        group = chars[i:i + 4]
        if len(group) < 4:
            break
        val = 0
        for c in group:
            val = val * 4 + BASE4[c]
        out.append(chr(val))
    return "".join(out)


def decode_core_values(b64_text):
    """宏吐出的超长 base64 解出来是“社会主义核心价值观”编码，
    再用在线工具/字典转成“南北绿豆”序列。这里只演示解码入口。"""
    return base64.b64decode(b64_text).decode("utf-8", "ignore")


if __name__ == "__main__":
    tail = extract_tail_hidden("text_for_4.txt")
    print("[*] base64 末 2bit 解出的后半段：", tail)

    # 用反推出的编码表演示解码（序列来自 VBA 宏解出的核心价值观文本）
    seq = ("南北南绿 南南南南 南北南南 南南南北 南绿豆绿 南绿南绿 北绿北北 "
           "南南绿绿 南绿南绿 南北绿绿 南南绿绿 南南南绿 南豆绿绿")
    head = decode_base4(seq)
    print("[*] 南北绿豆四进制解出的前半段：", head)
    print("[*] 两段按下划线拼接即最终 flag。")
