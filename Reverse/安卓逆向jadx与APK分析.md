# 安卓逆向：jadx 与 APK 分析

> **所属分类**：Reverse ｜ **难度参考**：简单
> **适用题型**：给一个 APK 文件，要求静态反编译找出校验逻辑并还原答案。

## 一、知识点原理讲解

### APK 的本质

APK 本质是一个 ZIP 包，里面包含：
- `classes.dex`：编译后的 Dalvik 字节码（核心逻辑在这里）。
- `resources.arsc` / `res/`：资源文件与字符串。
- `AndroidManifest.xml`：应用配置（入口 Activity、权限等）。

要拿逻辑就得把 `dex` 反编译回 Java/Kotlin 源码。

### 常用工具链

- **jadx-gui**：图形化反编译器，最常用。左侧包树 + 右侧反编译代码，支持搜索。
- **jadx**：命令行批量导出：`jadx app.apk -d out/`。
- **apktool**：解资源/Manifest（本题用不上）。
- **androguard**：脚本化分析。
- **frida**：动态 Hook（纯静态题用不上）。

### 校验逻辑的常见模式

安卓逆向入门题的校验函数通常长这样：

```kotlin
fun check(input: String): Boolean {
    if (input.length != CIPHER.size) return false       // 长度校验先于内容
    for (i in input.indices) {
        if ((input[i].code xor KEY) != CIPHER[i]) return false  // 逐字符异或
    }
    return true
}
```

要点：
- 加密是 `enc[i] = input[i] ^ key`，解密就是 `input[i] = enc[i] ^ key`（异或自逆）。
- `CIPHER` 是一个 `int[]` 数组，存的是每个字符异或 key 后的数值。
- **安卓里字符是 16 位 `char`**，异或的 key 可能大于 255（如 904 = 0x388），别当成字节异或。
- 长度校验往往先于内容校验，还原后位数要对上。

### 识别特征

- APK + `check(String)` 返回 boolean + 静态 `int[]` 大数组 = 异或校验题。
- 关键词搜索：`inputFlag`、`check`、`CIPHER`、`KEY`。

## 二、通用解题思路 / 套路

```
拿到 APK → jadx-gui 打开
→ 左侧包树找到主 Activity（通常 com.example.xxx → MainActivity）
→ 读 check() 校验函数，把校验式读成数学式：enc = f(input, key)
→ 对 f 求逆（异或自逆、加减可反推）
→ Python 批量还原 CIPHER 数组
→ 纯静态即可，不需要运行 App
```

**易错点**：
- 安卓字符是 16 位，key 可能 > 255。
- 长度校验先于内容校验，还原后位数要对上。
- 不要急着运行 App 动态调试——纯静态反编译通常就够了。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| jadx-gui | 官网下载 | 双击打开 APK，左侧包树导航 | 右侧显示反编译的 Java/Kotlin 源码 |
| jadx | 官网下载 | `jadx app.apk -d output_dir/` | 导出完整工程到目录 |
| Python 3 | 官网 | 对 CIPHER 数组逐个 `^ key` 转字符 | 打印还原字符串 |

## 四、实战例题

### 例题 1：jadx 反编译 + 异或校验反推

- 题型特征：给一个 debug 版 APK，主 Activity 有 `check(String)` 方法，内含长度检查和逐字符异或。
- 解题思路：
  1. jadx-gui 打开 APK，左侧导航 `com.example.包名 → MainActivity`。
  2. 读 `check()`：先比长度（须等于 CIPHER 数组长度），再循环 `(input.charAt(i) ^ 904) != CIPHER[i]`。
  3. 反推：`input[i] = CIPHER[i] ^ 904`。
  4. Python 对 CIPHER 数组每个值 `^ 904`，`chr()` 成字符拼接。
  5. 纯静态分析完成，不需要运行 App。
- 关键工具/脚本：`script/安卓逆向jadx与APK分析/solve.py`（CIPHER 数组逐个 XOR 904 拼字符串）；`../assets/images/安卓逆向jadx与APK分析/jadx_main.png`（jadx 反编译 MainActivity 的 check 方法）。
- 结果：得到 flag。
