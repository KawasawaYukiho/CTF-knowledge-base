# 个人网络安全 / CTF 知识体系

> 一个 CTF 个人知识库，按知识点/技术主题沉淀 Crypto、Misc、Reverse、Web、Pwn 各方向的原理、解题套路与工具使用
> 用于个人复习与持续积累

## 📖 这个仓库

- **按知识点/技术主题组织**：安全分类目录（Crypto / Misc / Reverse / Web / Pwn）下
每个目录内是按知识点命名的条目
- 每个知识点条目统一四节模板：**知识点原理讲解 → 通用解题思路/套路 → 工具使用 → 实战例题**；
靶场题目作为"例题"佐证知识点
- 保留有用的解题脚本和截图，按知识点归类于 `script/` 和 `assets/images/`

## 📁 仓库结构

```
CTF-knowledge-base/
├── README.md             
├── .gitignore
├── Crypto/      
├── Misc/        
├── Reverse/     
├── Web/        
├── Pwn/                 # 二进制：还没学
├── assets/images/<知识点>/
└── (Crypto|Misc|Reverse|Web)/script/<知识点>/    解题脚本
    (Misc|Reverse)/challenge/<知识点>/
```

## 🧭 浏览

1. **先看 README **：每个分类目录的 `README.md` 是该分类的**知识点索引**
每个知识点一行
2. **按需**：点进知识点条目，先看"知识点原理讲解"建立认知，再读"通用解题思路"掌握套路，照"工具使用"复现，最后用"实战例题"检验。

| 分类 | 知识点数 | 覆盖主题 | 入口 |
| --- | --- | --- | --- |
| Crypto 密码学 | 8 | 进制与编码转换、哈希爆破、RSA（基础/共享素数/代数分解）、XOR、Base64 变体与多层编码 | [Crypto/README.md](Crypto/README.md) |
| Misc 杂项/隐写/流量 | 18 | LSB 隐写、文件分离、PNG/JPEG/ZIP/二维码修复、频谱、GIF、Docker；流量重组、SQL 攻击链、DNS 隧道、日志、USB HID、pyc、docm、培根 | [Misc/README.md](Misc/README.md) |
| Reverse 逆向 | 12 | 查壳脱壳、静态/动态分析、花指令、迷宫、假 flag、PyInstaller；汇编阅读、XOR/RC4、SMC、安卓、Base64 换表 | [Reverse/README.md](Reverse/README.md) |
| Web | 3 | JWT 令牌、SQL 注入盲注、HTTP 方法覆盖 | [Web/README.md](Web/README.md) |
| Pwn 二进制 | 待补充 | — | [Pwn/README.md](Pwn/README.md) |

## 🔧 复现


- **Python 3.8+**，常用库：`pycryptodome`（RSA/AES）、`PIL`（图片处理）、`requests`（Web 脚本）。
- 常用外部工具（条目中注明）：Wireshark（流量）、zsteg / StegSolve（LSB 隐写）、binwalk / foremost（文件分离）、olevba（docm 宏）、DIE（查壳）、IDA Pro / x64dbg（逆向）、jadx（安卓）、pyinstxtractor / uncompyle6（PyInstaller 解包）、bkcrack（ZIP 已知明文攻击）

以 Crypto 一个知识点为例：

```bash
cd Crypto/script/RSA共享素数攻击
python calculate.py        # gcd 求共享素数并解密
```

## 📌 约定

- **条目模板**：见 [模板.md](模板.md)，新增知识点时直接复制模板结构（四节：原理讲解 / 通用思路 / 工具使用 / 实战例题）。
- **文件规范**：脚本只收有复用价值的 `.py`（≤30KB）；挑战源文件仅保留 ≤200KB 且对复现必需的；不收录解包产物、运行库、dll/pyd/exe/zip 等大体积文件。
- **命名**：条目用知识点名 `知识点.md`；脚本与截图按知识点归类重命名。
