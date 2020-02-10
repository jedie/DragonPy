ASM_CODE = """
db16 34 02                        PSHS A
db18 81 0d                        CMPA #000d(CR)                  IS IT CARRIAGE RETURN?
db1a 27 0b                        BEQ  NEWLINE                    YES
"""


class CodeLine:
    def __init__(self, code_values, statement, comment):
        self.code_values = code_values
        self.statement = statement
        self.comment = comment

    def __str__(self):
        code = ", ".join(["0x%02x" % i for i in self.code_values])
        if self.comment:
            return f"{code}, # {self.statement:<20} ; {self.comment}"
        else:
            return f"{code}, # {self.statement}"


start_addr = None
code_lines = []
for line in ASM_CODE.splitlines():
    line = line.strip()
    if not line:
        continue
    print(line)

    addr = line[:4].strip()
    if not addr:
        continue
    if start_addr is None:
        start_addr = addr
        print(f"start addr: {addr!r}")

    code = line[5:34]
    code_values = [int(i, 16) for i in code.split(" ") if i.strip()]
    print(" ".join(["%02x" % i for i in code_values]))

    statement = line[34:66].strip()
    print(f"{statement!r}")

    comment = line[66:].strip()
    print(f"{comment!r}")

    code_lines.append(
        CodeLine(code_values, statement, comment)
    )
    print()

print("-" * 79)
print("        self.cpu_test_run(start=0x4000, end=None, mem=[")
print(f"            # origin start address in ROM: ${start_addr}")
for code_line in code_lines:
    print(f"            {code_line}")
print("        ])")
