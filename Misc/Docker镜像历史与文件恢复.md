# Docker 镜像历史与文件恢复

> **所属分类**：Misc ｜ **难度参考**：偏难
> **适用题型**：给一个 `.tar`/Dockerfile 历史，题面说"删除过的文件不会真消失"。

## 一、知识点原理讲解

### 镜像分层与"删而不除"
Docker 镜像由多层只读 layer 叠加而成。Dockerfile 里常见：

```dockerfile
COPY note.txt avatar.png secret.zip /app/
RUN /bin/sh -c rm /app/note.txt /app/avatar.png /app/secret.zip
```

"删除"只是在最新一层里加了一条**白名单/墓碑**，让上层看不到这些文件；但**上一层（COPY 那一层）的文件内容字节仍完整躺在 tar blob 里**。因此可以遍历各层 blob，从删除前的那一层把文件恢复出来。

### 恢复要点
- `docker history --no-trunc` 先看清构建步骤：确认是"先 COPY、后 RUN rm"；
- `docker save` 导出镜像归档，解开后每层是一个 blob；
- 恢复目标文件要找对 **COPY 那一层（删除层的上一层）**，不是最终层。

### 常见后续
恢复出的文件常继续串联：PNG 尾部拼 WAV→频谱图取口令→OpenSSL 加盐 AES 密文解密。

## 二、通用解题思路 / 套路

```
拿到镜像 tar
→ docker load / docker history --no-trunc 看构建步骤
→ docker save 导出归档并解开
→ 遍历每层 blob: tar -tf 找含目标文件名的那一层
→ 单独解开该层，取出被删文件
→ 按文件类型继续（图片尾/频谱/加密）
```

易错点：
- 找对 COPY 层（删除层的上一层），不是最终层；
- base64 解出 `Salted__` 立刻想到 openssl enc 的 AES；
- AES 派生方式（PBKDF2/SHA256）要与题目一致。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| docker | 环境安装 | `docker history --no-trunc 镜像` | 看 COPY/RUN rm 步骤 |
| tar | 系统自带 | `tar -tf blob` / `tar -xf blob` | 列出/解开某层内容 |

```bash
docker load -i img.tar
docker save -o img2.tar 镜像
mkdir layers && tar -xf img2.tar -C layers
for f in layers/blobs/sha256/*; do
  tar -tf "$f" 2>/dev/null | grep -E "secret.zip|note.txt|avatar.png"
done
```

`script/Docker镜像历史与文件恢复/solve.py`：解析 `Salted__` 格式，按 PBKDF2(SHA256)/AES-256-CBC/PKCS7 解密（口令作参数传入）。运行：

```bash
cd script/Docker镜像历史与文件恢复
python solve.py <AES口令>      # 口令来自 note.txt 诗句提示
```

![docker history 看到先 COPY 后 RUN rm](../assets/images/Docker镜像历史与文件恢复/docker_history.png)

![逐层 blob 中找到含目标文件的那一层](../assets/images/Docker镜像历史与文件恢复/find_blob.png)

## 四、实战例题

### 例题 1：从镜像历史层恢复被删的提示/图片/压缩包
- 题型特征：一个 Docker 镜像 tar，题面明说"删除过的文件并不会真的消失"。
- 解题思路：`docker history --no-trunc` 确认先 COPY 三文件再 `RUN rm`；save 导出后遍历 `blobs/sha256`，用 `tar -tf | grep` 命中 COPY 那一层，单独解出被删的提示文本、头像 PNG、加密 zip。头像尾部再拼 WAV→频谱图取 zip 口令；解压得 `Salted__` 头密文，用提示文本诗句给出的口令做 AES-256-CBC 解密。
- 关键工具/脚本：`script/Docker镜像历史与文件恢复/solve.py`（Salted__ 格式 AES 解密）、`note.txt`（被删提示诗句）、`cipher.txt`（OpenSSL 密文）、`../assets/images/Docker镜像历史与文件恢复/docker_history.png`、`find_blob.png`（分层与定位过程）。
- 结果：AES 解密明文即为 flag。
