# PyInstaller 打包程序逆向

> **所属分类**：Reverse ｜ **难度参考**：中等
> **适用题型**：体积异常大的 Windows exe，DIE overlay 段能看到 `python3xx.dll`、`PYZ.pyz`，判定为 PyInstaller 打包的 Python 程序。

## 一、知识点原理讲解

### PE overlay 与 PyInstaller 结构

Windows PE 由 DOS Header → PE Header → 节表 → 各节原始数据组成；**最后一节结束之后的附加数据叫 overlay**。PyInstaller 把 Python 解释器（`python3xx.dll`）、标准库归档（`PYZ.pyz`）和自己脚本的 `.pyc` 全部附加在 overlay 里。

| 偏移位置 | 结构 | 说明 |
| --- | --- | --- |
| 文件开头 | DOS Header(64B) | `MZ` 开头，`0x3C` 处 `e_lfanew` 指向 PE 头 |
| e_lfanew 处 | PE Signature + FILE/OPTIONAL HEADER | 描述节表 |
| 其后 | Section Table | 每节 40 字节 |
| 节数据之后 | **OVERLAY** | PyInstaller 的 PYZ 与脚本字节码在此 |

PyInstaller **不对脚本做强加密**，解包即可拿回 `.pyc`。

### 两层可提取内容

1. **根目录入口脚本 `.pyc`**——`pyinstxtractor` 解包后直接出现在解包目录根；
2. **PYZ 归档 `PYZ.pyz`**——标准库与附加模块都打在这个 zlib 压缩归档里，是一个独立的 `.pyc` 包，不会自动散落到目录。若真正的校验模块在 PYZ 内，还需二次提取。

### pyc 结构与 marshal/dis 反汇编

`.pyc` 前 N 字节是头（magic number + flags + 时间戳/源哈希，长度随 Python 版本变化，常见为 16 字节），之后才是 marshal 序列化的 code object。反汇编必须先跳过头：

```python
import marshal, dis
f = open('xxx.pyc','rb')
f.read(16)                 # 跳 16 字节头（按版本调整）
code = marshal.load(f)      # 反序列化出 code object
dis.dis(code)               # 反汇编成可读指令
```

读 Python 字节码抓三类指令即可：`LOAD_CONST/STORE_NAME`（取常量、赋值）、`CALL`（调用 ord/chr/len）、`BINARY_OP`（下标、异或、拼接）。

### 两个常见坑

- **反编译器只吃单个 pyc**：直接对 `PYZ.pyz` 跑 uncompyle6/decompyle3 会报 `PYZ.pyz must point to a Python source ... or Python bytecode (.pyc)`，必须先从 PYZ 里把目标模块抽出来再反编译。
- **Python 版本要对齐**：pyc 的 magic number 与 marshal 格式随版本变化，版本不匹配会 `BadMagicNumber` 或反汇编错乱。pyinstxtractor 末尾会提示用哪个 Python 版本运行。

### 置换 + XOR 都可逆

还原出的加密形如 `output[i] = chr(ord(flag[table[i]]) ^ key)`：XOR 同常数两次即还原（对合）；`table` 是一个置换排列，逆运算就是"把输出第 i 位写回第 `table[i]` 位"。开一个等长数组按 `table` 归位即可，无需爆破。

## 二、通用解题思路 / 套路

```
大体积 exe → DIE overlay 见 python3xx.dll / PYZ.pyz → 判定 PyInstaller
→ pyinstxtractor.py 解包 → 拿到入口 pyc + 报告 Python 版本
→ 校验模块在根目录？
   → 是：直接 marshal+dis 反汇编入口 pyc
   → 否：用 ZlibArchiveReader 对 PYZ.pyz 二次提取全部模块 pyc
→ 抓 LOAD_CONST 抄出密文 / 置换表 / XOR_KEY
→ 按还原出的加密公式逆推（置换归位 + 异或）
→ 回代校验通过即得明文
```

易错点：
- pyc 头长度随版本变化，必须按对应版本跳头；不跳头直接 `marshal.load` 会读到 magic 报错。
- 别把 `*_extracted` 解包产物目录当成果提交，它只是中间产物。
- 版本不对（如用 Python 3.14 去 marshal 一个 3.12 的 pyc）会错乱。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| pyinstxtractor.py | GitHub 下载单文件 | `python pyinstxtractor.py xxx.exe` | 报告 PyInstaller 版本、Python 版本、入口 pyc，生成 `xxx.exe_extracted/` |
| marshal + dis | Python 标准库 | `f.read(16); dis.dis(marshal.load(f))` | 可读字节码指令流 |
| ZlibArchiveReader | `pip install pyinstaller` | 见 `script/PyInstaller打包程序逆向/solve_pyz_extract.py` | 从 PYZ.pyz 提取全部模块 code object |

## 四、实战例题

### 例题 1：一个 PyInstaller 打包、置换表 + 常量 XOR 的题

- 题型特征：大体积 exe，DIE overlay 段可见 `python3xx.dll` 与 `PYZ.pyz`。
- 解题思路：pyinstxtractor 解包，报告 Python 版本与入口 pyc；`f.read(16)` 跳头后 `marshal.load + dis.dis` 反汇编入口 pyc，从 `LOAD_CONST` 抄出密文（31 字节）、置换表（31 元素元组）、XOR 常数（55）。还原加密 `output[i]=chr(ord(input[table[i]])^55)`，逆运算 `ans[table[i]] = chr(ord(enc[i])^55)`，按表归位 join；回代 `enc(flag)==enc` 为 True。
- 关键工具/脚本：`script/PyInstaller打包程序逆向/solve.py`（按置换表归位 + XOR 逆推结果）、`script/PyInstaller打包程序逆向/encrypt.py`（从字节码还原的正向校验逻辑）、`script/PyInstaller打包程序逆向/PE文件结构.txt`、`py字节码.txt`、`反汇编.txt`（结构与反汇编笔记）、`../assets/images/PyInstaller打包程序逆向/decompress.png`（pyinstxtractor 解包结果）。
- 结果：归位后回代校验通过，得到 flag。

### 例题 2：一个需要对 PYZ.pyz 二次提取的 PyInstaller 题

- 题型特征：pyinstxtractor 报告 PyInstaller 2.1+、某 Python 版本、入口 pyc 在根目录，但真正的校验模块不在根目录。
- 解题思路：直接对 `PYZ.pyz` 反编译会报错；改用 `ZlibArchiveReader` 遍历 TOC 把全部模块 code object 抽成单独 `.pyc`，再对关键 pyc 做 `marshal.load + dis.dis`。注意用与打包时一致的 Python 版本运行，避免 BadMagic。
- 关键工具/脚本：`script/PyInstaller打包程序逆向/solve_pyz_extract.py`（从 PYZ.pyz 二次提取全部模块 pyc）、`script/PyInstaller打包程序逆向/solve_dis_pyc.py`（marshal+dis 反汇编关键 pyc）、`../assets/images/PyInstaller打包程序逆向/pyinstxtractor.png`（解包输出，含版本提示）、`../assets/images/PyInstaller打包程序逆向/uncompyle_fail.png`（直接对 PYZ 反编译报错的截图）。
- 结果：提取并反汇编关键模块，按还原逻辑逆推得到 flag。
