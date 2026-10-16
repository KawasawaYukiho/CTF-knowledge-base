# HTTP 方法覆盖

> **所属分类**：Web ｜ **难度参考**：入门
> **适用题型**：后端接口要求 `PUT`/`PATCH`/`DELETE`，但前端表单/浏览器只能发 `POST`，需要"借 POST 通道发别的方法"的接口题。

## 一、知识点

### 1.1 为什么会有方法覆盖

早期 HTML 表单只支持 `GET` 和 `POST` 两种方法，发不出 `PUT`、`PATCH`、`DELETE`
现代 RESTful 接口却常按方法区分动作（GET 查、POST 增、PATCH/PUT 改、DELETE 删）
为兼容浏览器这一限制，很多 Web 框架提供了**方法覆盖（Method Override）**机制：

- 客户端仍然发 `POST`；
- 但在请求头里声明"我真正想用的方法是另一个"；
- 服务端收到后，按声明的方法来路由处理

表面是 POST，实际被框架当成 PATCH/PUT/DELETE 执行

### 1.2 常用请求头

服务端约定好几个请求头别名，客户端任选其一：

```
X-HTTP-Method-Override: PATCH
X-Method-Override: PUT
X-HTTP-Method: DELETE
```

常见支持该机制的框架：Express（`method-override` 中间件）、Django、Rails、Laravel 等。

### 1.3 安全

如果服务端盲目信任这个请求头：

- 攻击者绕过前端限制，直接调用本应受限的 `PUT/DELETE/PATCH` 接口；
- 从而越权修改、删除他人资源；
- 题目考察：前端按钮禁用了某方法，需要自己发请求并加上覆盖头，然后绕过前端限制

### 1.4 特征

- 题目描述出现 "PATCH / PUT / DELETE" 提示"浏览器只能 POST" → 想到`method-override`
- 接口文档列出同一 URL 上挂着 GET/POST/PATCH 多个方法路由 → 试覆盖头
- 用 Burp Repeater 改方法被拒，但加请求头后成功 → 命中

## 二、通用

```
读题发现"后端要 PATCH、前端只能 POST"
→ 查接口文档/路径，定位真正受理答案的方法与路径（如 PATCH /api/check）
→ 先直接 POST 试探，确认被"临时通道受限"拒绝
→ 加方法覆盖请求头 X-HTTP-Method-Override: <目标方法>，body 照常带参数
→ 同时补 Content-Type，确保 body 被解析
→ 服务端按目标方法路由，校验参数正确 → 返回结果
```

通用步骤清单：

1. **先认清"真正受理的方法"**：接口文档里写 PATCH/PUT/DELETE 的那条路由，才是要打的。
2. **三个别名头都试一遍**：`X-HTTP-Method-Override`、`X-Method-Override`、`X-HTTP-Method`，不同框架认的名字不一样。
3. **body 与请求头缺一不可**：只发 POST 不加头会被拒；加了头但不带正确 body 也不行。
4. **记得补 Content-Type**：`application/x-www-form-urlencoded`，否则表单 body 不被解析。
5. **参数值按题目暗示猜**：这类题常要填"该技术的英文名称"，注意大小写与连字符（往往要求全小写、单词原形）。

易错点：

- 只发 POST 不加覆盖头，被临时通道拒绝。
- 参数值大小写/连字符写错（`Override` ≠ `override`）。
- 忘加 `Content-Type`，服务端收不到 body。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| curl | 系统自带 | `curl -X POST <目标> -H "X-HTTP-Method-Override: PATCH" -d "answer=xxx"` | 响应体即接口返回 |
| Burp Repeater / 浏览器插件 | 现成 | 手动加请求头、改 body 重放 | 看响应是否从"拒绝"变为"成功" |

典型命令：

```bash
curl -X POST "<目标>/api/check" \
     -H "X-HTTP-Method-Override: PATCH" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "answer=override"
```

> 说明：上例 `answer` 的取值是该技术的英文原名（全小写），按题目暗示填写；提交后响应即给出 flag。

## 四、实战例题

### 例题 1：后端要求 PATCH、前端只能 POST 的接口题

- 题型特征：场景描述"后端 API 必须用 PATCH 提交答案，但前端表单只能发 POST"；访问接口文档可见同一路径上 GET/POST/PATCH 分别承担不同职责，其中 PATCH 负责提交答案。
- 解题思路：
  1. 先直接 `POST` 该端点，被"临时通道受限"拒绝。
  2. 加上 `X-HTTP-Method-Override: PATCH` 请求头，仍用 POST 通道发送，body 带答案参数。
  3. 服务端按 PATCH 路由处理，校验参数正确后返回结果。
  4. 参数值按提示"这种技术的英文名称、全小写"确定为 `override`（注意 `Override`、`MethodOverride`、`method-override` 均不匹配，必须全小写原形）。
- 关键工具/脚本：`../assets/images/HTTP方法覆盖/request.png`（请求构造：POST 通道 + 覆盖头改为 PATCH + body 带答案参数的截图）。
- 结果：提交正确参数后得到flag。
