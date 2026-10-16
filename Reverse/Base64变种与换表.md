# Base64 变种与换表

> **所属分类**：Reverse ｜ **难度参考**：简单～中等
> **适用题型**：二进制中 strings 提取到以 `=` 结尾的密文和一张自定义 Base64 字母表，字母表与标准表顺序不同。

## 一、知识点原理讲解

### Base64 的本质：6 bit 查表

标准 Base64 把 3 字节（24 bit）拆成 4 个 6 bit 组，每组当作索引（0~63）去查一张 64 字符的表，得到 4 个输出字符。

**关键认知**：决定解码结果的是字符在表中的"位置"，不是字符本身。如果题目把表的字符顺序打乱（换表/移位），而你仍用标准表解码，就会解出乱码。

标准表：
```
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

### 常见换表方式

**1. ROT13 换表**（大小写字母各偏移 13，数字和 `+/` 不变）：
```
自定义：NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm0123456789+/
```
大写 A..M 挪到后面，N..Z 挪到前面——字母表偏移 13。小写同理。

**2. 凯撒分段移位**（大小写、数字分别移位不同量）：
```
运行时表：HIJKLMNOPQRSTUVWXYZABCDEFGtuvwxyzabcdefghijklmnopqrs4567890123+/
```
大写 +7、小写 -7、数字 +4、`+/` 不动。这种变换通常在程序启动时由初始化函数对 `b64_table` 原地改写。

### 正确的映射方向

设自定义表为 `custom`、标准表为 `std`。对密文里的字符 `c`：

1. 在 `custom` 里找到它的下标：`i = custom.index(c)`
2. 取 `std[i]`——这就是"如果用标准表，这个 6 bit 值本应对应哪个字符"
3. 把整串密文这样替换完，得到一串"标准 Base64"字符串
4. 用标准 `base64.b64decode` 解出原文

> **注意方向**：是 `std[custom.index(c)]`，不是反过来。

### 逆运算顺序

如果 Base64 解码后还有字节级变换（如 `enc = (input + 9) ^ 0x12`），逆运算必须**逆序**：

```
已知 enc = (input + 9) ^ 0x12
先去异或：  tmp = enc ^ 0x12
再去加法：  input = (tmp - 9) & 0xff   # 减完可能为负，&0xff 回绕到字节
```

顺序不能反。

### SSE 指令批量处理

IDA 中看到 `movd xmm0, 0x09090909` / `pshufd` / `paddb` / `pxor`，本质是编译器把"对前 16 个字节统一做同一算术/异或"向量化了，等价于后面的普通循环 `add eax,9; xor eax,0x12`。

## 二、通用解题思路 / 套路

```
file/strings 提取 → 发现 = 结尾的密文 + 一张完整 64 字符字母表
→ 对比标准表，识别换表规律（ROT13 / 凯撒移位 / 自定义重排）
→ 用 标准表[自定义表.index(c)] 把密文映射回标准 Base64
→ b64decode 得到中间字节
→ 若还有字节级变换，按逆序做逆运算（先抵消后发生的运算）
→ 补位符 = 按原长度补回去
```

**易错点**：
- 映射方向搞反（应是 `std[custom.index(c)]`）。
- 补位符 `=` 要按原长度补回去，别丢。
- 不要误以为"偏移 13"就是 ROT13 直接对密文做 ROT13——ROT13 作用在"表"上，不在密文字符上。
- 逆运算顺序：异或和加减要反向做（先抵消后发生的运算）。
- 减后可能为负，务必 `& 0xff` 回绕。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| strings | Linux / Git Bash | `strings file | grep "=="` | 提取密文、提示串、自定义字母表 |
| IDA Pro | 商业 | 反汇编找表初始化函数与字节变换函数 | 识别运行时表与加密公式 |
| Python 3 | 官网 | `base64.b64decode()` + 手写映射/逆运算 | 打印还原结果 |

## 四、实战例题

### 例题 1：ROT13 换表 Base64

- 题型特征：ELF 64-bit 可执行文件，`strings` 一次拿到密文、成功/失败提示和一张自定义 Base64 表。
- 解题思路：
  1. `file` 确认 ELF 类型（无需反编译）。
  2. `strings | grep` 出三行关键信息：密文（`=` 结尾）、成功提示、自定义字母表。
  3. 对比标准表：大小写字母段都是 ROT13 偏移 13，数字和 `+/` 不动。
  4. 逐字符 `std[custom.index(c)]` 把密文换成标准 Base64。
  5. `b64decode` 解出原文。
- 关键工具/脚本：`script/Base64变种与换表/solve_rot13_table.py`（按自定义表位置映射回标准表再解码）；`../assets/images/Base64变种与换表/strings.png`（strings 提取的密文与自定义表）。
- 结果：得到 flag。

### 例题 2：凯撒移位换表 + 逐字节线性变换

- 题型特征：PE32+ 程序，strings 提取到密文和函数名；启动时有初始化函数对 Base64 表做凯撒移位；校验函数对每字节做 `(input + 9) ^ 0x12`。
- 解题思路：
  1. `strings` 提取密文、提示串和函数名（`init_before_main`、`caesar_shift_table`、`b64_decode`、`crypto`）。
  2. 反汇编 `caesar_shift_table`，还原运行时表：大写 +7、小写 -7、数字 +4、`+/` 不动。
  3. 反汇编 `crypto`：前 16 字节用 SSE（`paddb +9`、`pxor 0x12`），后 10 字节循环同样逻辑，整体即每字节 `(input+9)^0x12`。
  4. 先按运行时表把密文映射回标准 Base64 并解码（得 26 字节）。
  5. 再逐字节逆运算：`((b ^ 0x12) - 9) & 0xff`。
- 关键工具/脚本：`script/Base64变种与换表/decode_caesar_table.py`（运行时表→标准表映射与 Base64 解码中间步骤）；`../assets/images/Base64变种与换表/b64_cipher_table.png`（.data 段中的密文与字母表）。
- 结果：得到 flag。
