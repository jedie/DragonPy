
with open("d64.rom", "wb") as out:
    with open("Dragon Data Ltd - Dragon 64 - IC17.ROM", "rb") as f:
        out.write(f.read())
    with open("Dragon Data Ltd - Dragon 64 - IC18.ROM", "rb") as f:
        out.write(f.read())

print out.name, "created."