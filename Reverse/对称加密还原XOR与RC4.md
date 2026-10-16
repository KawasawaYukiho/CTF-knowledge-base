# 对称加密还原：XOR 与 RC4

> **所属分类**：Reverse ｜ **难度参考**：入门～中等
> **适用题型**：逆向程序中识别出异或加密或 RC4 算法，从二进制中提取密文与密钥后用脚本还原明文。

## 一、知识点原理讲解

### 1. XOR（异或）——最基础的对称加密

异或运算的核心性质是**自逆**：`a ^ b ^ b = a`。因此加密和解密是同一个操作。

**单字节 XOR**：每个字节与一个固定常数异或。
```
enc[i] = plain[i] ^ key   ⟺   plain[i] = enc[i] ^ key
```
在反汇编中表现为 `xor reg, imm8`（如 `xor eax, 26h`）。

**循环 XOR**：密钥循环使用，即 `key[i % key_len]`。常见变体：
- 正序循环：`enc[i] = plain[i] ^ key[i % len]`
- 反转 key 循环：`enc[i] = plain[i] ^ key_reversed[i % len]`，对应下标形如 `key[len-1 - i%len]`。
- 只要看到 `i % N` 与 key 数组配合，就反应为循环异或。

### 2. RC4 —— 流密码

RC4 由两阶段组成：

**KSA（S 盒初始化）**：
```python
S = list(range(256)); j = 0
for i in range(256):
    j = (j + S[i] + key[i % len(key)]) % 256
    S[i], S[j] = S[j], S[i]
```

**PRGA（密钥流生成 + 加解密）**：
```python
i = j = 0
for b in ciphertext:
    i = (i + 1) % 256
    j = (j + S[i]) % 256
    S[i], S[j] = S[j], S[i]
    plain.append(b ^ S[(S[i] + S[j]) % 256])
```

**识别特征**：
- 一个长度 256 的数组初始化 `S[i] = i`；
- 第一个双层循环用 key 扰动交换 `S[i]`、`S[j]`；
- 第二个循环每次 `i++`、`j += S[i]`、swap、取 `S[(S[i]+S[j])%256]` 与输入异或。
- RC4 加解密对称，直接用同一 key 解密密文即可。

## 二、通用解题思路 / 套路

### XOR 类

```
IDA Shift+F12 找提示字符串交叉引用 → 进校验函数
→ 看到 xor reg, imm 或 key[i%len] ^ input[i] → 判定 XOR
→ 从 .rdata / 数据段抄出密文字节
→ 确定 key（常数或硬编码字符串），注意是否反转
→ Python 逐字节异或还原
```

### RC4 类

```
脱壳后 IDA 找校验函数
→ 见 256 长度数组初始化 + 双层交换循环 → 判定 RC4
→ 读出 key（通常硬编码字符串）与密文位置
→ 抄出密文字节，按 KSA+PRGA 模板写 Python 脚本解密
```

**易错点**：
- XOR 常数要看准十六进制（`26h` = 0x26）。
- 循环 XOR 的 key 要先反转再取模（若下标是 `len-1 - i%len`）。
- RC4 的 i、j 都要 `%256`，PRGA 里 swap 顺序别写反。
- 密文要抄全长度，漏字节会错位。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| IDA Pro | 商业 | `Shift+F12` 打开字符串窗口，双击提示串进交叉引用 | 定位校验函数 |
| DIE | 官网 | 打开 PE 查壳/导入表 | 确认是否加壳 |
| Python 3 | 官网 | 手写 XOR / RC4 解密脚本 | 打印还原明文 |

## 四、实战例题

### 例题 1：单字节 XOR 校验

- 题型特征：64 位 PE 无壳，校验函数中出现 `xor eax, 26h`，密文 31 字节在 `.rdata`。
- 解题思路：用 `Shift+F12` 找 `Enter flag:` 交叉引用进校验函数；识别单字节异或常数 0x26；从数据段抄出 31 字节密文；逐字节 `^ 0x26` 还原。
- 关键工具/脚本：`script/对称加密还原XOR与RC4/solve_xor_single_byte.py`（31 字节密文逐字节 ^0x26）；`../assets/images/对称加密还原XOR与RC4/xor_asm.png`（反汇编中的 `xor eax, 26h`）。
- 结果：得到 flag。

### 例题 2：循环 XOR + 反转密钥

- 题型特征：PE 中主流程是游戏化外壳，结束必弹一个格式正确的假 flag；字符串窗口里有一长串 hex 密文和一句英文提示。
- 解题思路：
  1. 假 flag 当干扰，不提交。
  2. `Shift+F12` 发现 hex 密文 + 提示串，交叉引用指向一个主流程不调用的死代码函数。
  3. 伪代码核心：`v2 = key[14 - i%15] ^ input[i]`——`14` = 15-1，即 key 反转后循环取。
  4. 逆运算：`flag[i] = enc[i] ^ reversed_key[i%15]`。
- 关键工具/脚本：`script/对称加密还原XOR与RC4/solve_xor_reversed_key.py`（key 反转后与 hex 密文逐字节 XOR）。
- 结果：得到 flag。

### 例题 3：RC4 对称解密

- 题型特征：UPX 加壳但节名伪装成 VMP0/VMP1，脱壳后校验函数是标准 RC4 结构。
- 解题思路：
  1. DIE 查壳报 UPX，但节名是 VMP0/VMP1；二进制里能搜到 `UPX!` 标记 → 节名伪装的 UPX。
  2. 用十六进制编辑器把节名改回 UPX0/UPX1，`upx -d` 脱壳。
  3. IDA 反汇编认出 KSA + PRGA 两段循环 = RC4；key 为硬编码字符串。
  4. 从 `.rdata` 抄出 27 字节密文，按 RC4 对称解密。
- 关键工具/脚本：`script/对称加密还原XOR与RC4/decode_rc4.py`（KSA+PRGA 解密密文）；`../assets/images/对称加密还原XOR与RC4/cipher_rdata.png`（.rdata 段密文位置与 memcmp 校验）。
- 结果：得到 flag。
