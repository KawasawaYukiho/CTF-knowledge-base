# -*- coding: utf-8 -*-
# 培根密码（Baconian cipher）通用解码器
# 规则：A=0、B=1，每 5 个字符为一组，对应一个 5 位二进制，查表映射到 A-Z。
# 本题：卡面底部一串 A/B 字符分组解码得到压缩包密码。

# 培根表：5 位组合 -> 字母（I/J、U/V 合并是经典培根，这里用常见 26 字母版）
BACON = {
    "AAAAA": "A", "AAAAB": "B", "AAABA": "C", "AAABB": "D", "AABAA": "E",
    "AABAB": "F", "AABBA": "G", "AABBB": "H", "ABAAA": "I", "ABAAB": "J",
    "ABABA": "K", "ABABB": "L", "ABBAA": "M", "ABBAB": "N", "ABBBA": "O",
    "ABBBB": "P", "BAAAA": "Q", "BAAAB": "R", "BAABA": "S", "BAABB": "T",
    "BABAA": "U", "BABAB": "V", "BABBA": "W", "BABBB": "X", "BBAAA": "Y",
    "BBBAA": "Z",
}

def bacon_decode(s: str) -> str:
    s = "".join(s.split()).upper()          # 去掉空白/换行，统一大小写
    out = []
    for i in range(0, len(s) - len(s) % 5, 5):
        out.append(BACON.get(s[i:i + 5], "?"))
    return "".join(out)

if __name__ == "__main__":
    sample = "AABBAAABBBABBBABAABABAABBBAA ABABAAAAAABAABABA"  # 卡面 A/B 串（示例）
    print(bacon_decode(sample))             # 输出解压密码（本题为 GHOSTRICK）
