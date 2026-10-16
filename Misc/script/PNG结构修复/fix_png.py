# -*- coding: utf-8 -*-
"""
PNG 结构修复解题脚本
ctfer.png 的 IHDR 高度被人改小，导致 CRC 校验失败、图片打不开。
PNG 结构：
  89 50 4E 47 0D 0A 1A 0A | IHDR chunk(长度4 + 'IHDR' + 13字节数据 + CRC4)
  IHDR 数据: 宽度4 高度4 bitdepth1 colortype1 compression1 filter1 interlace1
  IHDR chunk 的 CRC 覆盖 [类型'IHDR' + 13字节数据]。
修复思路：固定其它字段，只爆破“高度”这 4 字节，使 CRC32 等于文件里记录的 CRC。
修复后图片上的文字即为 flag。
"""
import struct
import zlib


def fix_png_height(path_in, path_out):
    data = bytearray(open(path_in, "rb").read())
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    # IHDR chunk 从偏移 8 开始
    p = 8
    length = struct.unpack(">I", data[p:p + 4])[0]
    ctype = data[p + 4:p + 8]
    assert ctype == b"IHDR"
    ihdr = data[p + 8:p + 8 + length]          # 13 字节 IHDR 数据
    stored_crc = struct.unpack(">I", data[p + 8 + length:p + 12 + length])[0]

    width = struct.unpack(">I", ihdr[0:4])[0]
    # 高度在 IHDR 的 4..8 字节
    for h in range(1, 0xFFFF):
        cand = ihdr[:4] + struct.pack(">I", h) + ihdr[8:]
        if zlib.crc32(b"IHDR" + cand) & 0xFFFFFFFF == stored_crc:
            data[p + 12:p + 16] = struct.pack(">I", h)  # 写回正确高度
            open(path_out, "wb").write(data)
            print(f"[*] CRC 匹配，正确高度 = {h} (0x{h:X})，已写出 {path_out}")
            return h
    print("[-] 未找到匹配高度")
    return None


if __name__ == "__main__":
    # 用法：python fix_png.py ctfer.png fixed.png
    import sys
    if len(sys.argv) < 3:
        print("用法: python fix_png.py <ctfer.png> <fixed.png>")
    else:
        fix_png_height(sys.argv[1], sys.argv[2])
