# -*- coding: utf-8 -*-
"""
USB HID 键盘流量解题脚本
USB HID Boot 键盘报文 -> Usage ID -> 按键字符。
报文固定 8 字节：[修饰键][保留0][UsageID1..UsageID6]。
本题每个报文只有第 3 字节(Byte2)非零，按两行一组(按下/释放)取按下的 UsageID。
在 0x29(Esc) 处切两段：
  - 之前：先按 i 进入插入模式，再敲出 5x5 字母矩阵；
  - 之后：Vim 普通模式 hjkl 移动光标，从左上角 g 出发记录途经字符。
两段拼接结果即为 flag。
"""

# USB HID Usage ID -> 字符（Boot 键盘常用子集）
USAGE = {
    0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e', 0x09: 'f',
    0x0a: 'g', 0x0b: 'h', 0x0c: 'i', 0x0d: 'j', 0x0e: 'k', 0x0f: 'l',
    0x10: 'm', 0x11: 'n', 0x12: 'o', 0x13: 'p', 0x14: 'q', 0x15: 'r',
    0x16: 's', 0x17: 't', 0x18: 'u', 0x19: 'v', 0x1a: 'w', 0x1b: 'x',
    0x1c: 'y', 0x1d: 'z',
    0x28: '\\n', 0x29: '[ESC]', 0x2c: ' ',
}


def parse(path):
    """usb_data.txt 每行形如: 00:00:0c:00:00:00:00:00  i
    取第 3 个字节(Byte2)作为按下的 UsageID。"""
    keys = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if not ln or ":" not in ln:
            continue
        hexpart = ln.split()[0]
        b = [int(x, 16) for x in hexpart.split(":")]
        if len(b) >= 3 and b[2] != 0:
            keys.append(b[2])
    return keys


def letters_only(keys):
    """只保留字母 UsageID(0x04..0x1d)，过滤空格(0x2c)/回车(0x28)/Esc(0x29)。"""
    return [k for k in keys if 0x04 <= k <= 0x1d]


def main():
    keys = parse("usb_data.txt")
    # 在 Esc(0x29) 处切分
    esc = keys.index(0x29)
    before, after = keys[:esc], keys[esc + 1:]

    # 还原 5x5 矩阵：Esc 之前的按键里，第一个字母是 i(进入插入模式的命令)，
    # 去掉它之后正好 25 个字母，排成 5x5。
    all_letters = letters_only(before)
    matrix_flat = all_letters[1:]            # 跳过开头的插入命令 i
    grid = [[USAGE[matrix_flat[i * 5 + j]] for j in range(5)] for i in range(5)]
    print("[*] 还原出的 5x5 字母矩阵：")
    for row in grid:
        print("   ", " ".join(row))

    # hjkl 移动(UsageID): k=0x0e上 j=0x0d下 h=0x0b左 l=0x0f右，起点左上角(0,0)=g
    move = {0x0e: (-1, 0), 0x0d: (1, 0), 0x0b: (0, -1), 0x0f: (0, 1)}
    r, c = 0, 0
    path = [grid[r][c]]
    for k in after:
        if k in move:
            dr, dc = move[k]
            nr, nc = r + dr, c + dc
            if 0 <= nr < 5 and 0 <= nc < 5:  # 越界的 k/h 无新增字符
                r, c = nr, nc
                path.append(grid[r][c])
    print("[*] 光标途经字符拼接：", "".join(path))


if __name__ == "__main__":
    main()
