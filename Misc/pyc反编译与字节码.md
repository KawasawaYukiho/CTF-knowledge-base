# pyc 反编译与字节码

> **所属分类**：Misc ｜ **难度参考**：简单
> **适用题型**：拿到一个 `.pyc` 字节码文件，要求还原源码并从中取出被藏起来的字符串（常是 ASCII 数字数组或一段 Web 利用链演示）。

## 一、知识点原理讲解

### 1. pyc 是什么

`.pyc` 是 Python 把 `.py` 源码编译后的**字节码缓存**，用来加快模块加载。它不是源码，但可以反编译回 Python 代码。Python 3.7+ 的文件结构：

```text
[4 字节 magic number][4 字节 bit field][4 字节 mtime][4 字节 源码大小][marshal 序列化的 code object]
```

开头的 **magic number** 标识 Python 版本（不同版本 magic 不同），选反编译工具时要与之匹配。

### 2. 反编译工具链

| 工具 | 说明 |
| --- | --- |
| `uncompyle6` | 老牌，支持 Python 2.7 ~ 3.8 |
| `decompyle3` | uncompyle6 的 fork |
| `pycdc` | C++ 编写，支持较新版本 |
| `dis` / `marshal` | 标准库，手动反汇编 / 读 code object |
| `strings` | 兜底，直接提取文件里的明文字符串 |

版本差太多时 `marshal.load` 会报错；用 `uncompyle6`（内部 xdis 兼容多版本）或换 `pycdc`。

### 3. 两类常见"藏数"手法

- **大段教学/迷惑代码**：反编译后可能先演示 Web SSTI 利用链，如 `"".__class__.__mro__` → `object` → `__subclasses__()` → 从某子类 `__init__.__globals__['__builtins__']` 里取 `chr` 函数。这是 Web 注入的前置知识，在 Misc 题里往往是**教学演示段，不是结果本身**。
- **真正的结果：ASCII 数字数组**：源码末尾常有一整段纯整数列表，数字全部落在可打印 ASCII 范围（32~126）。识别特征：**看到一整段都在 32~126 的整数列表，基本就是 ASCII**，逐个 `chr()` 再拼接即可。

```python
codes = [ ... ]                  # 一串小整数
flag = "".join(chr(c) for c in codes)
```

## 二、通用解题思路 / 套路

```
拿到 .pyc → file 识别为 Python 字节码（看 magic number 定版本）
  → uncompyle6 / pycdc 反编译出完整 .py
  → 通读，区分"教学/迷惑段"和"真正取数段"
  → 末尾一整串 32~126 的整数 → 逐个 chr() 拼接
  → 得结果
```

- 别被大段 SSTI 教学代码带偏，结果常在最后几行。
- Python 版本不匹配会反编译失败，换 pycdc 或对应 uncompyle6 版本。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| file | 系统自带 | `file x.pyc` | 识别为 Python bytecode + magic 版本 |
| uncompyle6 | `pip install uncompyle6` | `uncompyle6 x.pyc` | 直接还原出 .py 源码 |
| pycdc | 编译安装 | `pycdc x.pyc` | 新版本字节码的备用反编译器 |
| Python 脚本 | 标准库 | `script/pyc反编译与字节码/ascii_codes.py` | 通用"整数列表 → chr 拼接"还原 |

运行方式：

```bash
uncompyle6 challenge/pyc反编译与字节码/what_is_pyc.pyc   # 还原源码
python script/pyc反编译与字节码/ascii_codes.py            # 把 codes 数组 chr() 拼接
```

## 四、实战例题

### 例题 1：反编译 pyc，末尾 ASCII 数字数组还原出结果

- 题型特征：直接给一个 `.pyc` 文件。
- 解题思路：先 `file` 识别为 Python 字节码，用 `uncompyle6` 反编译出完整源码；前半段是 SSTI 继承链（`__class__ → __mro__ → object → __subclasses__ → 找 __builtins__ → 取 chr`）的教学演示，理解即可；重点看末尾一整串落在 32~126 的整数列表 `codes`，逐个 `chr()` 拼接即结果。
- 关键工具/脚本：`challenge/pyc反编译与字节码/what_is_pyc.pyc`（待反编译的挑战文件）、`script/pyc反编译与字节码/ascii_codes.py`（整数列表 → chr 拼接的通用还原）。
- 结果：得到 flag。
