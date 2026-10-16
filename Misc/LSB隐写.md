# LSB 隐写

> **所属分类**：Misc ｜ **难度参考**：入门
> **适用题型**：一张看似正常的无损位图（PNG/BMP），命名带 lsb/steg，无其他附件，却要用像素最低位藏东西。

## 一、知识点原理讲解

### 原理
PNG/BMP 的每个像素由若干字节表示颜色（如 RGB 各 1 字节）。一个字节的**最低有效位（LSB，bit 0）**翻转，对人眼感知的颜色几乎没有影响（红色从 200 变 201 肉眼难分辨）。于是可以把秘密信息的每个 bit，依次写进每个像素字节的 bit 0 里——这就是 LSB 隐写。

载体图片看起来完全正常，但把所有像素的 bit 0 按某种顺序抽出来拼好，就是隐藏的数据。常见做法是把秘密字节按位展开，逐像素填入。

### 关键可调参数（决定能否正确还原）
- **通道**：只取 R、只取 G、只取 B，还是 RGB 全取；
- **位平面**：取 bit 0（最常见）还是 bit 1、bit 2……；
- **扫描方向**：按行（Row）还是按列（Column）；
- **位序**：每个字节内低位在前（LSB First）还是高位在前（MSB First）；
- **字节平面顺序**：RGB、RBG、GRB、GBR、BRG、BGR 等排列。

这些参数组合错了就会读出乱码，需要按组合尝试。命中时 hex dump 开头往往就是 `66 6c 61 67`（即 `flag{` 的 ASCII）。

### 常见变体
- 只藏在单个通道（如仅蓝色通道）；
- 藏在 bit 1/bit 2 而非 bit 0；
- 同样原理可迁移到 BMP、WAV、AVI 等无损载体。

## 二、通用解题思路 / 套路

```
拿到一张正常 PNG，无附加文件、命名带 lsb/steg
→ 先自动扫：zsteg 直接遍历所有通道/位平面
→ 没命中再手动 SteSolve：勾 RGB 三通道 bit 0
→ Extract By=Row、Bit Order=LSB First、Bit Plane Order=RGB
→ Preview 出 hex dump，看到 66 6c 61 67（flag{）开头即命中
→ hex 按字节转 ASCII，忽略尾部 00 填充
```

易错点：
- Bit Order（LSB/MSB First）和通道顺序（RGB/BRG 等）选错会乱码，必须组合尝试；
- 尾部 `00` 是填充位，忽略；
- 别忘记 zsteg 能自动扫，比手工逐个参数试快得多。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| zsteg | `gem install zsteg` | `zsteg hidden.png` | 自动列出各通道/平面命中的 `text:` 内容 |
| SteSolve (stegsolve.jar) | 官网下载，需 Java | 打开图片 → Analyse → Data Extract | 勾选 bit 平面/通道，Preview 右侧 hex+ASCII |

SteSolve 提取参数对照：

| 参数 | 常用取值 | 含义 |
| --- | --- | --- |
| Bit Planes | R/G/B 的 bit 0 全勾 | 只取最低位平面 |
| Extract By | Row（按行） | 逐像素扫描方向 |
| Bit Order | LSB First | 字节内低位在前 |
| Bit Plane Order | RGB | R→G→B 顺序取字节 |

脚本化提取（PIL）：

```python
from PIL import Image
im = Image.open("carrier.png").convert("RGB")
bits = []
for r, g, b in im.getdata():
    bits += [r & 1, g & 1, b & 1]          # RGB 各取最低位
# 把 bits 每 8 个拼成一个字节，再 decode
```

## 四、实战例题

### 例题 1：一张命名暗示"懂不懂 LSB"的单图 Misc 题
- 题型特征：一张看似完全正常的 PNG，无任何附加文件，命名与"LSB/懂不懂"相关。
- 解题思路：图片查看器与 `file` 均无异常，怀疑像素隐写；用 SteSolve 勾 RGB 三通道 bit 0、Row、LSB First、RGB 顺序，Preview 直接出现以 `flag{` ASCII 开头的 hex dump，转 ASCII 即得结果。
- 关键工具/脚本：复现载体 `challenge/LSB隐写/doyouknow.png`（待提取的 PNG）；SteSolve GUI（本题无独立 .py 脚本）。
- 结果：得到 flag。

### 例题 2：流量包还原出的小 PNG 上做 LSB 提取
- 题型特征：从 pcap 流量里重组出一个完整 ZIP，解压得到一张很小的 PNG。
- 解题思路：先用流量手段（HTTP 自定义头拿口令、Follow TCP Stream Raw 拼包）还原出 `hidden.png`；该图体积仅 2KB 却要藏信息，直接 `zsteg hidden.png` 自动扫各通道最低位平面，命中 `text:` 一行即为结果。
- 关键工具/脚本：`zsteg hidden.png`（自动遍历位平面，免去手工对齐参数）。
- 结果：得到 flag。
