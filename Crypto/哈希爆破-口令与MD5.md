# 哈希爆破：口令与 MD5

> **所属分类**：Crypto ｜ **难度参考**：入门
> **适用题型**：Linux shadow 口令文件还原、已知前缀+约束下的 MD5 暴力枚举、小空间哈希反推

## 一、知识点原理讲解

### 1.1 哈希函数的"不可逆"与"可爆破"边界

MD5、SHA-256 等密码学哈希函数把任意长度输入压缩成固定长度摘要，**没有反函数**，理论上不能从摘要反推原文。但"不可逆"不等于"不可破"：

- 如果**未知输入空间很小**，攻击者可以把所有候选输入都算一遍哈希，与目标比对——命中即得原文。这就是"爆破/字典攻击"。
- 哈希能否被爆破，取决于**未知信息的熵大小**（字符集 × 长度），而不是算法本身强弱。

常见可爆破场景：6 位纯数字口令（10⁶ = 100 万种）、末尾 4 位小写字母（26⁴ ≈ 45 万种）等。

### 1.2 Linux shadow 文件格式与加盐哈希

`/etc/shadow` 存储系统用户口令哈希，每行格式：

```
用户名:$id$salt$hash
```

- `$id$`：标识算法族。`$1$`=MD5-crypt、`$5$`=SHA256-crypt、`$6$`=SHA512-crypt；题目"自研"方案可能用其他 `$id$` 并在题干里直接告知算法。
- `salt`：随机盐，参与哈希以避免相同口令产生相同摘要、抵御彩虹表。
- `hash`：盐与口令按约定方式混合后做哈希的结果（小写十六进制）。
- 口令字段为单个 `!` 的行表示账户被锁定。

加盐哈希的设计初衷是抵御彩虹表，但**不能阻止小空间穷举**——盐虽然随机，但它和 hash 一起明文放在文件里，攻击者直接拿到。

### 1.3 爆破的核心逻辑

凡是"已知哈希 + 已知盐 + 已知口令空间"的题，本质都是小空间穷举匹配：

```
对每个候选口令 candidate：
    算 hash = H(salt + candidate)
    if hash == target_hash: 命中，candidate 就是明文
```

## 二、通用解题思路 / 套路

```
识别特征（文件名 shadow/passwd + 行格式 xxx:$数字$盐$哈希 → 口令文件题；
         或 给一段已知串 + 哈希值 + 未知部分字符集/长度 → 小空间枚举题）
→ 第一步：读懂题目自述的哈希公式（一轮还是多轮？盐在前还是后？）
→ 第二步：估算未知空间大小（字符集^长度），确认可控
→ 第三步：枚举所有候选，逐个算哈希与目标比对
→ 第四步：命中即得明文，按题目规定格式包裹后提交
```

**易错点清单：**

- 盐要和文件里给出的完全一致，拼接顺序（salt+pwd 还是 pwd+salt）要按题目定义，不能想当然。
- 补零不能少：6 位数字口令必须 `zfill(6)`，否则 `0` 和 `000000` 对不上。
- 标准 SHA256-crypt 不是一轮哈希，遇到真实 `/etc/shadow` 的 `$5$`/`$6$` 要用 hashcat 对应模式，别套一轮公式。
- 比对用 `hexdigest()` 的字符串形式，别和 `digest()` 的字节形式混用。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| Python `hashlib` | 内置 | `hashlib.sha256(data.encode()).hexdigest()` / `hashlib.md5(s.encode()).hexdigest()` | 返回小写十六进制摘要字符串 |
| Python `itertools.product` | 内置 | `product(ascii_lowercase, repeat=4)` | 笛卡尔积枚举所有长度为 4 的小写字母组合 |
| `str.zfill(n)` | 内置 | `"0".zfill(6)` → `"000000"` | 左侧补零到固定位数 |
| hashcat（可选） | 官网下载 | `hashcat -m 1400 -a 3 hash.txt ?d?d?d?d?d?d` | `$5$`/`$6$` 等标准 shadow 哈希的专业爆破工具 |

典型代码块（一轮 SHA256 + 6 位数字口令）：

```python
import hashlib

salt = "<从文件读出的 salt>"
target_hash = "<从文件读出的 hash>"

for i in range(1000000):
    password = str(i).zfill(6)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    if h == target_hash:
        print("口令:", password)
        break
```

## 四、实战例题

### 例题 1：Linux shadow 加盐哈希口令爆破

- 题型特征：给出 `shadow` 和 `shadow.bak` 两个口令文件，其中 alice 行格式为 `alice:$7$<salt>$<hash>`，题目说明算法是一轮 `SHA256(salt + password)`，且口令为 6 位纯数字。
- 解题思路：按 `$` 切分取出 salt 和 target_hash；枚举 000000~999999 共 100 万种 6 位数字口令，逐个计算 `SHA256(salt + password)` 的十六进制摘要，与目标比对；命中即得口令。两个文件互相校验结果一致。
- 关键工具/脚本：`script/哈希爆破/crack.py`（用 shadow.bak 的 salt/hash 爆破）、`script/哈希爆破/crack2.py`（用原件 shadow 的 salt/hash 爆破，互相校验）；`../assets/images/哈希爆破/shadow_bak.png`（shadow.bak 中 alice 行的盐与哈希截图）。
- 结果：得到 flag。

### 例题 2：已知前缀的 MD5 小空间枚举

- 题型特征：给出 flag 的已知前缀字符串 + 完整 MD5 十六进制值，说明末尾 4 位均为小写字母。
- 解题思路：用 `itertools.product` 枚举全部 26⁴ ≈ 45 万种 4 位小写字母后缀；对每种"前缀+后缀"算 MD5 摘要，与目标比对；命中即得完整 flag。
- 关键工具/脚本：`script/哈希爆破/md5_brute.py`（枚举 4 位小写后缀，比对 MD5 还原完整 flag）。
- 结果：得到 flag。
