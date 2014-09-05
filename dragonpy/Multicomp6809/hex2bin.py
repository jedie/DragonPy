
"""
"""

IN_FILENAME = "EXT_BASIC_NO_USING.hex"
OUT_FILENAME = "EXT_BASIC_NO_USING.bin"

def iter_steps(g, steps):
    """
    iterate over 'g' in blocks with a length of the given 'step' count.

    >>> for v in iter_steps([1,2,3,4,5], steps=2): v
    [1, 2]
    [3, 4]
    [5]
    >>> for v in iter_steps([1,2,3,4,5,6,7,8,9], steps=3): v
    [1, 2, 3]
    [4, 5, 6]
    [7, 8, 9]

                                 12345678        12345678
                                         12345678
    >>> bits = [int(i) for i in "0101010101010101111000"]
    >>> for v in iter_steps(bits, steps=8): v
    [0, 1, 0, 1, 0, 1, 0, 1]
    [0, 1, 0, 1, 0, 1, 0, 1]
    [1, 1, 1, 0, 0, 0]
    """
    values = []
    for value in g:
        values.append(value)
        if len(values) == steps:
            yield list(values)
            values = []
    if values:
        yield list(values)

print("Read %s" % IN_FILENAME)
hex_file = open(IN_FILENAME, "r")

out_bytes = []

for line in hex_file:
    #~ print line
    line = line.strip()
    data = line[9:-2]
    #~ print data
    for byte_hex in iter_steps(data, steps=2):
        byte_hex = "".join(byte_hex)
        #~ print byte_hex,
        codepoint = int(byte_hex, 16)
        byte = chr(codepoint)
        out_bytes.append(byte)
    #~ print
hex_file.close()


# Display only the dump:
length = len(out_bytes)
print("length: %i $%02x" % (length, length))
pos = 0xc000
print("ORG: $%04x" % pos)
steps = 32
for bytes in iter_steps(out_bytes, steps=steps):
    line = " ".join("%02X" % ord(b) for b in bytes)
    if "10 CE  1 EE" in line or "X7E E5  0" in line:
        print("*"*79)
    print("$%4x %s" % (pos, line))
    if "10 CE  1 EE" in line or "X7E E5  0" in line:
        print("*"*79)
    pos += steps



print("Write to %s..." % OUT_FILENAME)
bin_file = open(OUT_FILENAME, "wb")
bin_file.write("".join(out_bytes))
bin_file.close()
print("OK")
