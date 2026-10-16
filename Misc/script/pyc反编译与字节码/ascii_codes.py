# -*- coding: utf-8 -*-
# "数字数组转 ASCII" 通用还原脚本
# 识别特征：反编译/反汇编后若出现一整段都在 32~126 之间的整数列表，
#           几乎一定是可打印字符的 ASCII 码，用 chr() 逐个转再拼接即可。

def codes_to_str(codes) -> str:
    return "".join(chr(c) for c in codes)

if __name__ == "__main__":
    demo = [104, 101, 108, 108, 111]      # 示例：hello 的 ASCII 码，演示 chr() 用法
    print(codes_to_str(demo))             # 实际使用时替换为反编译出的 codes
