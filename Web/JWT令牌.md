# JWT 令牌

> **所属分类**：Web ｜ **难度参考**：简单
> **适用题型**：登录/认证类 Web 题，登录成功后 Cookie、Authorization 头或 localStorage 里出现三段式 `xxx.yyy.zzz` 字符串。

## 一、知识点原理讲解

### 1.1 什么是 JWT

JWT（JSON Web Token）是一种无状态的身份令牌。登录成功后服务端签发它，之后客户端每次请求都带上它，服务端验签后即认定身份。它本身**不是加密**，而是一个可被任何人公开解码的签名结构——"签名"只防篡改，不防阅读。

一个 JWT 由三部分用 `.` 连接，三部分都是 **Base64URL** 编码（可安全放在 URL/Cookie 中，无需填充对齐）：

```
eyJhbGciOi... . eyJzdWIi... . SflKxwRJS...
   Header          Payload        Signature
```

- **Header**：声明签名算法与 token 类型，例如 `{"alg":"HS256","typ":"JWT"}`。
- **Payload**：存放 claims（声明），如 `username`、`exp`（过期时间）等业务字段。**这一段是明文 Base64URL，任何人都能解开看内容。**
- **Signature**：用 Header 指定的算法（如 HS256）对"Header.Payload"做签名，服务端持有密钥可验证 token 有没有被改过。

### 1.2 为什么"解码不需要密钥"

这是最容易踩的认知误区：

- **解码（decode）是公开操作**：把第一段、第二段直接 Base64URL 解开就能看到 JSON，不涉及密钥。
- **签名验证（verify）才需要密钥**：服务端用密钥重算签名，与第三段比对，判断 token 是否被篡改。

所以看到 JWT，第一件事不是猜密钥，而是**先把 payload 解开看看里面藏了什么**——很多题把答案、提示、内嵌编码就放在 payload 字段里。

### 1.3 payload 里常藏的二次编码

解开 payload 后，某个 claim 的值往往不是明文，而是另一种编码。按字符集特征识别：

| 编码 | 字符集特征 | 典型长度/填充 |
| --- | --- | --- |
| Base64 | 大小写字母 + 数字 + `+/` | `=` 结尾补齐 |
| Base32 | 仅大写字母 `A–Z` + 数字 `2–7` | `=` 补齐到 8 的倍数 |
| Base58 | 无 0/O/I/l，字母数字混排 | 无填充 |
| Hex | `0–9 a–f` | 偶数长度 |

payload 里出现全大写字母 + 数字 + `=` 结尾的串，基本可判为 Base32，用 `base64.b32decode()` 解即可。

### 1.4 配套考点：登录前的时间戳窗口校验

JWT 题的"前置门"经常是一个登录校验。一种高频套路是：页面源码注释里泄露了服务端逻辑，要求提交一个"接近服务器当前 Unix 秒级时间戳"的密码，例如差值小于 5 秒即放行。

关键在于**不能用本机时间**：本机时钟和服务器时钟往往差几秒到几分钟，直接填本地 `Date.now()` 会被判"错过时机"。正确做法是先随便发一个请求，从响应头 `Date`（HTTP 标准头，即服务器自己的当前时间）取出时间，再换算成 Unix 秒级时间戳提交——这是最直接、最可信的"服务器时钟"来源。

### 1.5 识别特征速查

- 登录成功后 Cookie / Authorization / localStorage 出现 `xxx.yyy.zzz` 三段串 → JWT。
- payload 解开后出现全大写 + `=` 结尾 → Base32；出现 `+/` → Base64。
- 登录页文案含 "moment / time / 时机"，或源码注释里出现 `time.time()` / `int()` → 时间戳窗口校验，优先取服务器 `Date` 头。

## 二、通用解题思路 / 套路

```
登录成功拿到三段式 token
→ 把 token 放到 jwt.io（或本地 base64url 解码）解 Header + Payload
→ 通读 payload 每个字段，找"不像身份信息"的可疑字段（如 gift / secret / data）
→ 对可疑值按字符集识别编码（base32/base64/hex/base58）并层层解码
→ 解出的内容即目标（flag 或下一步口令）
```

通用步骤清单：

1. **F12 看全量前端信息**：HTML 注释、内联 JS、隐藏表单字段、Network 请求与响应——服务端校验逻辑常以注释形式直接泄露。
2. **登录后必查存储**：Cookie、localStorage、sessionStorage、响应头 Set-Cookie，JWT 是高频落点。
3. **payload 当明文读**：不要把 JWT 当加密，见怪不怪直接解。
4. **嵌套编码层层剥**：外层 JWT 解出的字符串再按字符集继续解。
5. **时间类题目只信服务器**：用响应头 `Date` 反推服务器时间，不信本机时钟。

易错点：

- 把 JWT 签名当成加密，以为没有密钥就看不到内容。
- 本地时钟不同步导致时间戳窗口登录失败。
- 登录跳转后 Network 面板找不到原请求的 Cookie——记得勾"保留日志"。

## 三、工具使用

| 工具 | 安装 | 常用用法 | 输出解读 |
| --- | --- | --- | --- |
| jwt.io | 网页在线工具 <https://jwt.io/> | 把 JWT 粘进左侧，右侧即解出 Header/Payload | Decoded Payload 里的字段即明文 claims |
| CyberChef | 网页在线工具 | 搜 "Base32 Decode"，把可疑串贴入 | 解出可读字符串即为嵌套内容 |
| Python base64 | 自带 | `python -c "import base64;print(base64.b32decode('<串>').decode())"` | 打印解码后的明文字符串 |

典型命令（对 payload 中识别出的 Base32 串解码）：

```bash
python -c "import base64; print(base64.b32decode('<payload 中的可疑串>').decode())"
```

## 四、实战例题

### 例题 1：一个带时间戳登录门、登录后发 JWT 的 Web 题

- 题型特征：登录页文案暗示"时机稍纵即逝"，F12 源码注释里泄露了"提交值与服务器时间戳差值小于某秒数"的校验逻辑。
- 解题思路：
  1. 先用本地 Unix 时间戳登录，提示"错过时机"，判断本机时钟与服务器不同步。
  2. 发请求取响应头 `Date`，换算成服务器 Unix 秒级时间戳填入密码框提交，登录成功。
  3. 从响应 Set-Cookie 里拿到三段式 token（JWT）。
  4. jwt.io 解码 payload，发现一个 `gift` 字段为全大写 + `=` 结尾的串，判为 Base32。
  5. Base32 解码该串得到一段字符串，即目标。
- 关键工具/脚本：
  - `../assets/images/JWT令牌/set_cookie.png`：登录成功后 Set-Cookie 中出现 token 的截图。
  - `../assets/images/JWT令牌/decode.png`：jwt.io 解码 payload，`gift` 字段为 Base32 串的截图。
- 结果：解码得到flag。
