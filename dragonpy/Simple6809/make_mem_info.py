
"""
"""

IN_FILENAME = "ExBasROM.LST"

rom_list = open(IN_FILENAME, "rb")

out_bytes = []

for line in rom_list:
    #~ print line
    line = line.strip()
    items = [x.strip() for x in line.split()]
    addr = line[5:9].strip()
    if not addr:
        continue

    line = line.replace("\x97", "-")
    line = line.replace("\x91", "'")
    line = line.replace("\x92", "'")
    line = line.replace("\x93", '"')

#     line = line.decode("ASCII", "replace")
#     line = line.decode("ASCII", "strict")
#     print line
    desc = line[50:]
    desc = desc.split(" ", 1)
    desc = desc[-1]
    desc = desc.strip()
    if not desc or desc in ("*",):
        continue
    print('        (0x%s, 0x%s, %r),' % (addr, addr, desc))
#     print items
#     print
rom_list.close()


