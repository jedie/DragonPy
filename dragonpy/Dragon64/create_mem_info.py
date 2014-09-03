


with open("Dragon 64 in 32 mode.txt", "r") as f:
    for line in f:
        line=line.strip()
        if not line or line.startswith("#"):
            continue

        #~ print line
        addr, comment = line.split(";",1)

        addr = addr.strip()
        comment = comment.strip("* ")
        addr = addr.replace("$","0x")

        try:
            start_addr, end_addr = addr.split("-")
        except ValueError:
            start_addr = addr
            end_addr = addr


        comment = comment.replace('"','\"')
        print('        (%s, %s, "%s"),' % (start_addr, end_addr, comment))