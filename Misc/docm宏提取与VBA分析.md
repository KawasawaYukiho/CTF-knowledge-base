# docm 宏提取与 VBA 分析

> **所属分类**：Misc ｜ **难度参考**：偏难
> **适用题型**：给一个启用宏的 Word 文档（.docm），要求提取 VBA 宏并运行/阅读其吐出的数据，常结合 Base64 变体隐写与"已知前缀反推编码表"。

## 一、知识点原理讲解

### 1. docm vs docx，以及怎么提宏

`.docm` 与 `.docx` 都是 OOXML（本质是一个 zip 包），区别只是 **docm 允许内嵌 VBA 宏**。宏二进制固定在 `word/vbaProject.bin`。提取流程：

```bash
# 把 .docm 改名/复制成 .zip 解压
pip install oletools
olevba word/vbaProject.bin > vba_code.txt
```

宏里常见一种"吐出超长 Base64"的子过程：用 `&=` 把一大段 base64 拼接，再 `Selection.TypeText` 输出——直接读 `vba_code.txt` 即可拿到整串，或在 Word 里 `Alt+F8` 运行宏。

### 2. Base64 尾部 2bit 隐写（重点）

Base64 把 3 字节（24bit）拆成 4 个 6bit 字符。当明文不是 3 的倍数时，最后一个 base64 字符只贡献前 4bit，**后 2bit 恒为补 0**——这 2bit 的"空位"就被用来藏秘密。

做法：让**多行 base64 的明文完全相同**，只改最后一个有效字符，于是每行末字符的低 2bit 就是 1 个 2bit 块：

| 末字符 | base64 索引 | 6bit | 低 2bit |
| --- | --- | --- | --- |
| `9` | 61 | 111101 | `01` |
| `/` | 63 | 111111 | `11` |
| `+` | 62 | 111110 | `10` |
| `8` | 60 | 111100 | `00` |

把 N 行末字符的低 2bit 依次串起来，每 8bit 切一个 ASCII 字符，即得隐藏段。

### 3. 用已知前缀反推编码表（四进制/多符号编码）

遇到"核心价值观 / 南北绿豆 / 风花雪月"这类把符号折叠成少数几个字的编码，本质是**低进制（如四进制 base4）**：每 4 个符号 = 8bit = 1 个 ASCII 字符。

关键技巧：**用已知前缀反推编码表**。题目通常提示结果以某固定前缀开头，已知该前缀每个字符的 8bit 二进制，对照前几组符号即可推出每个符号的数值，再整段解码。反推时要逐 bit 对齐（4 符号 = 1 字节），不能凭感觉猜。

## 二、通用解题思路 / 套路

```
.docm 改名解压 → word/vbaProject.bin → olevba 提宏
  → 读宏里超长 base64 → 解码 → 常是"价值观/多字符号"编码
  → 用已知 flag 前缀反推符号表 → 解出结果前半段
另一路：文档里的二维码/图片 → 扫出多行"几乎相同"的 base64
  → 取每行末字符低 2bit → 串成字节 → 解出结果后半段
  → 两段拼接
```

- 见到 docm 先 `olevba`。
- 见到"多行几乎相同的 base64"就查末字符低 2bit。
- 末字符要先去掉 `=` 填充再取 base64 索引。
- 见到多符号编码，先用已知前缀反推编码表再解码。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| olevba | `pip install oletools` | `olevba word/vbaProject.bin` | 导出 VBA 宏全文 |
| Python 脚本 | 标准库 | `script/docm宏提取与VBA分析/solve.py` | base64 末 2bit 提取 + 多符号四进制解码 |
| 提取出的素材 | — | `script/docm宏提取与VBA分析/vba_code.txt`、`text_for_4.txt` | 宏全文 / 二维码扫出的 base64 行 |

运行方式：

```bash
cd script/docm宏提取与VBA分析
python solve.py
```

## 四、实战例题

### 例题 1：docm 宏吐 Base64 + 二维码 Base64 尾 2bit，双路拼接

- 题型特征：一个带宏的 Word 文档 + 多张叠图，题面与"base"相关。
- 解题思路：把 .docm 当 zip 解压，对 `word/vbaProject.bin` 用 olevba 提宏；宏吐出一段超长 base64，解码后是"价值观类多符号编码"，用已知结果前缀反推出每个符号的数值（四进制），每 4 符号拼 1 字节解出前半段。另一路：文档里某张图是二维码，扫码得到 N 行前缀完全一致、仅末字符不同的 base64，逐行取末字符低 2bit 串成字节解出后半段；两段拼接即结果。
- 关键工具/脚本：`script/docm宏提取与VBA分析/solve.py`（末 2bit 提取 + 四进制解码）、同目录 `vba_code.txt`（olevba 提取的宏全文）、`text_for_4.txt`（二维码扫出的 base64 行）；截图见 `../assets/images/docm宏提取与VBA分析/qrcode.png`（藏 base64 行的二维码）。
- 结果：得到 flag。
