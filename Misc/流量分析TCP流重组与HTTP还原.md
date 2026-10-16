# 流量分析：TCP 流重组与 HTTP 还原

> **所属分类**：Misc ｜ **难度参考**：简单
> **适用题型**：给一个/多个 `.pcap`、`.pcapng`，要求从网络流量里还原被隐藏的口令、文件、POST 数据或找出"谁做了某个操作"。

## 一、知识点原理讲解

### 1. 为什么流量需要"重组"

以太网/IP 流量在 Wireshark 里默认按**一个个数据包**显示，但一个 HTTP 响应、一个文件下载，会被 TCP 拆成很多个 segment 分片传输。单独看任何一个分片都不完整，必须把**同一条 TCP 连接的双向载荷按顺序拼起来**，才能还原出原始的 HTTP 请求/响应或被传输的文件。Wireshark 的 **Follow TCP Stream（追踪 TCP 流）** 就是自动帮你做这件事。

关键点：另存时显示方式必须选 **Raw（原始数据）**。若选 ASCII / HEX，文本里的转义、二进制字节会被破坏，拼出来的文件就损坏了。

### 2. HTTP 请求/响应里藏东西的常见位置

- **自定义请求头**：除 `Host`、`Content-Type` 等标准头外，请求可带任意自定义头（如 `X-Password`、`X-Token`）。过滤 `http` 后逐行看请求头，凡是"非标准命名 + 像 base64 串（字母数字、`/+`、末尾 `=`）"都值得解一下。
- **POST body**：表单以 `application/x-www-form-urlencoded` 提交，body 形如 `a=1&b=2`。其中敏感字段（`secret` 等）常被 **URL 编码**：`{` = `%7B`、`}` = `%7D`。不解码会漏。
- **Request Method 差异**：一堆访问里，`GET` 只是浏览页面，真正的动作往往是唯一的 `POST`。找"谁干了某事"时，先按方法分类锁定唯一的 POST。

### 3. 识别被传输文件的"魔数"

拼出的原始字节流要先判断它是什么文件，常见签名：

| 签名（十六进制） | 文件类型 |
| --- | --- |
| `89 50 4E 47` | PNG |
| `FF D8 FF` | JPEG |
| `50 4B 03 04` (`PK\x03\x04`) | ZIP 本地文件头 |
| `50 4B 05 06` (`PK\x05\x06`) | ZIP 结束记录(EOCD) |

看到 `PK\x03\x04` 开头就说明拼出的是个 ZIP，往往还需要解压口令——口令通常就藏在前面分析出的 HTTP 头里。

## 二、通用解题思路 / 套路

```
拿到 pcap / pcapng
  → 过滤 http，逐行看请求/响应头与请求方法
  → 发现自定义头 / 唯一 POST / 不完整的文件下载
  → 自定义头 base64 解码（常见是解压口令）
  → 对目标 TCP 连接 Follow → TCP Stream → 显示选 Raw → 另存为文件
  → file / 魔数确认文件类型（PK 开头=zip）
  → 用前面解出的口令解压，得到最终载体（图片等）
  → 对图片跑 LSB 工具（zsteg / stegsolve）拿结果
```

- 只浏览（GET）的人/包通常是干扰项，唯一的 POST、自定义头、异常大的响应才是关键。
- POST body 里的 `{}` 常被编码成 `%7B%7D`，要 URL 解码。
- 文件被拆进两个甚至多个 pcap 时，要在每个包里分别找属于它的流，再合并。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| Wireshark | 官网下载 | 过滤栏输 `http`；选中包右键 Follow → TCP Stream / HTTP Stream；显示改 Raw → Save As | 还原出完整会话/原始文件字节 |
| tshark | Wireshark 自带 | `tshark -r x.pcap -Y http -T fields -e http.request.line` | 批量导出 HTTP 头/字段 |
| zsteg | `gem install zsteg` | `zsteg hidden.png` | 列出 PNG/BMP 各通道各 bit 平面隐写内容，`text:` 行即结果 |
| Python 脚本 | 标准库 | 见 `script/流量分析TCP流重组与HTTP还原/solve.py` | 无 GUI 时纯 Python 拼 TCP 载荷并按 `PK` 切出 zip |

典型手动流程：

```text
Wireshark 打开 pcap → 过滤 http
  → 右键目标连接 → Follow → TCP Stream → 右下角显示下拉选 "Raw" → Save As secret.zip
  → file secret.zip   # 确认是 Zip archive
```

## 四、实战例题

### 例题 1：两个 pcap 分片还原出一个带口令 ZIP，再 LSB 取结果

- 题型特征：给两个小 pcap，一个含口令线索、一个含不完整的文件下载；暗示"另一个包才能提取"。
- 解题思路：先在第一个包过滤 `http`，从自定义请求头 `X-Password` 拿到一段 base64，解码即 ZIP 口令；再到第二个包里选中该 TCP 连接，Follow → TCP Stream，显示选 **Raw**，另存为 zip（文件头 `PK\x03\x04` 可确认）；用口令解压得到一张 PNG；最后对 PNG 跑 `zsteg` 扫最低有效位（LSB）拿到结果。
- 关键工具/脚本：`script/流量分析TCP流重组与HTTP还原/solve.py`（纯 Python 遍历 pcap 解出口令、从 TCP 流拼出 zip）、同目录 `flow_1.pcap`、`flow_2.pcap`、解压得到的 `hidden.png`；截图见 `../assets/images/流量分析TCP流重组与HTTP还原/x_password.png`（自定义头）、`../assets/images/流量分析TCP流重组与HTTP还原/tcp_stream.png`（追踪 TCP 流）、`../assets/images/流量分析TCP流重组与HTTP还原/find_zip.png`（`PK` 头确认 zip）。
- 结果：得到 flag。

### 例题 2：HTTP 会话追踪，从 POST body 的 URL 编码字段取结果

- 题型特征：给一份 Web 访问流量，要求找出"谁做了某个动作"并从表单字段取数据。
- 解题思路：过滤 `http`，按 Request Method 区分——绝大多数是 `GET` 浏览，只有唯一一个 `POST` 是真正动作；定位该 POST 包，读 body，`secret` 字段值被 URL 编码，`%7B`→`{`、`%7D`→`}` 解码即结果。复现流量：`challenge/流量分析TCP流重组与HTTP还原/snack_traffic.pcapng`。
- 关键工具/脚本：Wireshark 图形操作为主；核心是 `http` 过滤 + Follow HTTP Stream 读 body + URL 解码。
- 结果：得到 flag。
