# SMC 自修改代码

> **所属分类**：Reverse ｜ **难度参考**：中等
> **适用题型**：PE 文件静态反汇编某段是乱码但运行正常，导入表含 VirtualProtect，程序运行时才解密代码段。

## 一、知识点原理讲解

### 什么是 SMC

SMC（Self-Modifying Code，自修改代码）是反静态分析的常用手段：程序把关键代码段加密存储，运行时在内存中解密后再执行。静态分析者看到的全是乱码字节，无法直接反汇编。

### 为什么静态分析会失效

CPU 取指时，`.text` 段默认权限是"可读可执行但不可写"（`PAGE_EXECUTE_READ`）。要在运行时修改自己的代码，必须先：

1. 调用 `VirtualProtect(addr, size, PAGE_EXECUTE_READWRITE, &old)` 把目标内存改成"可写可执行"；
2. 用循环把这段内存里的字节逐个解密（通常是 XOR 或加减）写回原地址；
3. 再跳过去执行。

因此 **看到 `VirtualProtect` + 一个对 `.text` 段地址做字节级循环改写的函数，就是 SMC 解密 stub**。

### SMC 解密 stub 的典型结构

```asm
push 0x40          ; PAGE_EXECUTE_READWRITE
push 0x1000        ; 4KB 粒度
push 0x401080      ; 目标地址 = .text 段内
call [VirtualProtect]

; 循环 N 次：
mov  edx, 目标地址
add  edx, [循环计数器]
movsx eax, byte ptr [edx]
xor  eax, 0x90     ; 解密 key（通常是单字节 XOR）
mov  [目标地址 + 计数器], al
loop ...
```

三个关键参数需要从 stub 中读出：
- **目标地址**：被加密的代码段起始位置。
- **循环次数**：加密了多少字节。
- **解密 key**：通常是单字节 XOR 常数。

### 手动模拟解密的方法

不需要让程序真正运行。直接在 IDA 的 Hex View 里抄出加密字节，在 Python 中用同样的 key 解密，然后把还原后的字节在 IDA 中重新反汇编（先 Undefine，再按 C）。

## 二、通用解题思路 / 套路

```
DIE/IDA 导入表看到 VirtualProtect → 判定 SMC 嫌疑
→ 找到对代码段做字节循环改写的函数 = 解密 stub
→ 从 stub 读出：目标地址 / 循环次数 / XOR key
→ Hex View 抄出目标地址起 N 个加密字节
→ Python 模拟解密（同 key XOR）
→ 还原后的字节丢回 IDA 重新反汇编
→ 读出真实校验逻辑（比较常量、分支等）
→ 运行程序输入答案验证
```

**易错点**：
- 不要在静态乱码上硬读指令——那是加密后的字节，不是代码。
- 解密 key 要从 stub 里读准（如 0x90），循环次数也要数对（如 0x24 = 36）。
- 解密 stub 往往在入口/main 之前被调用，先于真实校验函数执行。
- 还原后要在 IDA 里 Undefine 再反汇编，否则残留旧数据类型导致错误。

## 三、工具使用

| 工具 | 安装 | 常用命令 / 参数 | 输出解读 |
| --- | --- | --- | --- |
| DIE | 官网 | 打开 PE → Import 视图 | 导入表中出现 VirtualProtect = SMC 特征 |
| IDA Pro | 商业 | 导入表双击 VirtualProtect 看交叉引用；Hex View 跳地址抄字节；Undefine 后按 C 重新反汇编 | 控制流图显示"改权限→循环→解密体→恢复权限"四块 |
| Python 3 | 官网 | 对抄出的加密字节列表逐个 `^ key` | 打印还原后的机器码 hex |

## 四、实战例题

### 例题 1：VirtualProtect + XOR 解密代码段

- 题型特征：PE32 程序，DIE 导入表第一行就是 VirtualProtect；某段代码静态反汇编是乱码，但程序能正常运行。
- 解题思路：
  1. DIE 导入表确认 VirtualProtect → 判定 SMC。
  2. IDA 中双击 VirtualProtect 交叉引用，定位解密 stub（约 `0x4010B0`）。控制流图清晰分为"改权限 → 循环判定（36 次）→ 循环体（每字节 XOR 0x90）→ 恢复权限"四块。
  3. Hex View 跳到目标地址（`0x401080`），抄出 36 个加密字节。
  4. Python 每个字节 `^ 0x90` 解密。
  5. 把还原后的字节在 IDA 里重新反汇编，得到标准函数：`cmp dword ptr [ebp+8], 0x3039`——即判断输入是否等于 12345。
  6. 运行程序输入 12345 验证通过。
- 关键工具/脚本：`script/SMC自修改代码/decrypt.py`（36 个加密字节 XOR 0x90 还原机器码）；`../assets/images/SMC自修改代码/die_virtualprotect.png`（DIE 导入表中的 VirtualProtect）；`../assets/images/SMC自修改代码/ida_smc_stub.png`（SMC 解密 stub 控制流图）；`../assets/images/SMC自修改代码/hex_401080.png`（Hex View 中的加密字节）；挑战文件见 `challenge/SMC自修改代码/teach_smc.exe`。
- 结果：得到 flag。
