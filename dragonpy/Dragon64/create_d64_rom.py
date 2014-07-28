
with open("d64.rom", "wb") as out:
    with open("d64_ic17.rom", "rb") as f: # "Dragon Data Ltd - Dragon 64 - IC17.ROM"
        out.write(f.read())
    with open("d64_ic18.rom", "rb") as f: # "Dragon Data Ltd - Dragon 64 - IC18.ROM"
        out.write(f.read())

print out.name, "created."