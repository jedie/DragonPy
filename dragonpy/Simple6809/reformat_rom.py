
"""
    insert the destination address to all lables in ExBasROM.LST
"""

IN_FILENAME = "ExBasROM.LST"

print("Read %s" % IN_FILENAME)
lst_file = open(IN_FILENAME, "r")

OUT_FILENAME = IN_FILENAME + "2"
new_lst_file = open(OUT_FILENAME, "w")

addr_dict = {}
for line in lst_file:
#     print line
#     continue
    
    line = line.replace("\x97", "-")
    line = line.replace("\x91", "'")
    line = line.replace("\x92", "'")
    line = line.replace("\x93", '"')

    addr = line[5:9].strip()
#     print repr(addr)
    if addr:
        desc = line[59:]
        code = line[:59]
#         print code, desc

        lable = line[29:39].strip()
        if lable:
#             print repr(lable)
            addr_dict[lable] = addr

        dst_raw = line[44:59] # .strip()
#         print repr(dst_raw)

        dst = dst_raw.strip()
        dst = dst.lstrip("#")
        dst = dst.split("+", 1)[0]
        dst = dst.split("-", 1)[0]

        print(repr(dst), addr_dict.get(dst, "-"))

        if dst in addr_dict:
            print("%r -> %r" % (dst, addr_dict[dst]))
            print("1:", code)
            new_dst = "%s(%s)" % (addr_dict[dst], dst)
            code = code.replace(dst, new_dst)
            print("2:", code)
            print()

        line = "%-70s %s" % (code, desc)

    line = line[5:] # cut line number
    line = line.rstrip()
#     print repr(line)

#     print line
    new_lst_file.write(line + "\n")

lst_file.close()
new_lst_file.close()

print("\nnew file %r written." % OUT_FILENAME)
