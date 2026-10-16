# -*- coding: utf-8 -*-
# DNS 隐蔽信道（DNS exfiltration）还原脚本
# 思路：异常 DNS 查询名由一串 Base32 子域名分段拼成，去掉点号拼成整串后
#       Base32 解码 -> zlib 解压，即还原出被外传的配置文本。
import base64, zlib

# 来自 pcap 中固定尾缀 t.events.app-analytic 之前的 4 段子域名
qname = ("PDNBLSSBBLBDAECA2F6U4ELRFW2E3CRFK5IAITYQYZSGZC3VGJGGEFOFXNVZN77."
         "TWYNJQ52NVMZMVCXCSTLJZJBYHVMGWVDGTFU2YM2CQGOB4EVQ2YPUDTWPETI6TU."
         "523G745XF5B4BR4VLCETQLTIUSNZEE4XYXDA7ZC6TPFH5DNXGZLMY75UUUZGD45."
         "B6JCKM2L75KD6LXSLAQ")

b32 = qname.replace(".", "")                    # 去点，把分段子域名拼成整串
b32 += "=" * ((8 - len(b32) % 8) % 8)           # Base32 按 8 字节补齐 padding
data = zlib.decompress(base64.b32decode(b32))   # Base32 解码 + zlib 解压
print(data.decode())                            # 还原出 application.yml
