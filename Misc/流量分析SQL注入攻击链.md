# 流量分析：SQL 注入攻击链识别

> **所属分类**：Misc ｜ **难度参考**：中等
> **适用题型**：给一份 Web 服务器 HTTP 流量，要求事后复盘攻击者干了什么、从哪条响应里取到敏感文件内容。

## 一、知识点原理讲解

### 1. 为什么要在流量里认攻击链

真实 Web 攻击不是单条请求，而是一串有先后顺序的请求：探测 → 探测列数 → 爆表 → 写文件 → 执行命令。把这些请求按**时间线**连起来读，就是一条完整的入侵链。Misc 题把它做成"事后取证"：给你服务器抓到的 HTTP 包，让你当一回蓝军/复盘者。

### 2. 怎么一眼认出攻击者

过滤 `http` 后对比正常用户与异常源：

- 正常浏览器 User-Agent 是 `Mozilla/5.0 ... Chrome ...`。
- 攻击者往往用脚本扫，UA 是 `python-requests/x.y.z`、`sqlmap/...`，并且**短时间内向同一站点发出大量请求**，payload 里全是 SQL 语句。

锁定后用 `ip.src == <异常IP> and http` 只看这个 IP 的全部请求。

### 3. 一条典型的 SQL 注入 → 写马 → 读文件链

按请求时间线常见如下步骤（URL 中的空格多为 `%20`，引号为 `'`）：

1. `id=5'` —— 加单引号探测注入点，看是否报错；
2. `id=-1 union select 1,2,3` —— union 探列数与回显位；
3. `union select 1,database(),version()` —— 爆库名、版本；
4. `union select group_concat(table_name) from information_schema.tables` —— 爆表名；
5. `into outfile '/var/www/html/uploads/shell.php'` —— 用文件写入函数把一句话木马落到 web 目录；
6. 访问 `/uploads/shell.php?cmd=ls`、`cmd=cat /flag` —— 通过木马执行系统命令读文件。

**结果在响应体，不在请求行**：`cmd=cat` 那条请求的服务器响应，往往再做一层 Base64，`base64 -d` 解码才是答案。

## 二、通用解题思路 / 套路

```
pcap → 过滤 http
  → 找 UA=python-requests / sqlmap 的异常 IP（攻击者）
  → ip.src==该IP and http 聚焦其全部请求
  → 按时间线还原：单引号探测 → union 爆表 → into outfile 写马 → cmd 执行
  → 定位 cmd=cat 读敏感文件 那条请求
  → Follow HTTP Stream 看响应体 → 若为 base64 则 base64 -d 解码
```

- 不要只看单条包，攻击链断在单包里就找不到答案。
- 答案在**响应体**；响应常常做 Base64，看到一长串字母数字 `=` 结尾就先解码。
- 识别关键字：`union`、`information_schema`、`into outfile`、`cmd=`。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| Wireshark | 官网 | 过滤 `http`；`ip.src==x and http`；选中包右键 Follow → HTTP Stream | 看到攻击者全部请求/响应 |
| tshark | Wireshark 自带 | `tshark -r x.pcap -Y "http and ip.src==x" -T fields -e http.request.uri` | 批量导出攻击者请求 URI |
| base64 | 系统自带 | `base64 -d resp.txt` | 解出响应体原文 |

复现文件：`challenge/流量分析SQL注入攻击链/challenge.pcap`（约 159KB）。

## 四、实战例题

### 例题 1：从 HTTP 流量还原"注入→写马→读文件"完整攻击链

- 题型特征：给一份含大量访问的 pcap，要求找出攻击 IP 并取到服务器上某文件的内容。
- 解题思路：过滤 `http`，对比 User-Agent 找出 UA 为 `python-requests`、持续发注入 payload 的异常 IP；用 `ip.src==该IP and http` 聚焦其全部请求，按时间线读出"加单引号探测 → union select 爆列/爆库/爆表 → into outfile 写一句话木马 → 访问木马执行 `cmd=cat`"的链条；定位 `cmd=cat` 读敏感文件那条请求，Follow → HTTP Stream 看响应体，是一段 Base64，解码即结果。
- 关键工具/脚本：`challenge/流量分析SQL注入攻击链/challenge.pcap`；截图见 `../assets/images/流量分析SQL注入攻击链/筛选.png`（按攻击者 IP 过滤后的 HTTP 请求列表）。
- 结果：得到 flag。
