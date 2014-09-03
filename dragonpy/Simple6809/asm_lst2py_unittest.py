

ASM_CODE = """
db16 34 02                        PSHS A
db18 81 0d                        CMPA #000d(CR)                  IS IT CARRIAGE RETURN?
db1a 27 0b                        BEQ  NEWLINE                    YES
"""

class CodeLine(object):
    def __init__(self, code_values,statement,comment):
        self.code_values=code_values
        self.statement=statement
        self.comment=comment

    def __str__(self):
        code = ", ".join(["0x%02x" % i for i in self.code_values])
        if self.comment:
            return "%s, # %-20s ; %s" % (
                code,self.statement,self.comment
            )
        else:
            return "%s, # %s" % (code,self.statement)

start_addr = None
code_lines = []
for line in ASM_CODE.splitlines():
    line=line.strip()
    if not line:
        continue
    print(line)

    addr = line[:4].strip()
    if not addr:
        continue
    if start_addr is None:
        start_addr = addr
        print("start addr: %r" % addr)

    code = line[5:34]
    code_values = [int(i,16) for i in code.split(" ") if i.strip()]
    print(" ".join(["%02x" % i for i in code_values]))

    statement = line[34:66].strip()
    print("%r" % statement)

    comment = line[66:].strip()
    print("%r" % comment)

    code_lines.append(
        CodeLine(code_values, statement, comment)
    )
    print()

print("-"*79)
print("        self.cpu_test_run(start=0x4000, end=None, mem=[")
print("            # origin start address in ROM: $%s" % start_addr)
for code_line in code_lines:
    print("            %s" % code_line)
print("        ])")