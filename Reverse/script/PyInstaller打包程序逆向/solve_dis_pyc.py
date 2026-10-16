import marshal, dis

path = r"<解包输出目录>\sub_114514.pyc"

with open(path, "rb") as f:
    header = f.read(16)   # Python 3.14 的 pyc 头长度需确认
    print("Header:", header.hex())
    code = marshal.load(f)

dis.dis(code)