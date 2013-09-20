"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
from CPU6809Instructions import ADDRES_MODE_DICT, OP_CATEGORIES, OP_DATA, OPERANT_DICT
import pprint

# def get_group_by_category(data):
#     result = {}
#     for opcode, op_data in data.items():
#         category_id = op_data["category"]
#         op_data["opcode"] = opcode
#         result.setdefault(category_id, []).append(op_data)
#     return result
#
# op_data = get_group_by_category(OP_DATA)

print "class CPU6809(object):"

data = {}
for op_data in OP_DATA:
#     print op_data
    category = op_data.pop("category")
    data.setdefault(category, {})
    category_dict = data[category]

    instruction = op_data.pop("instruction")
    category_dict.setdefault(instruction, {})
    instruction_dict = category_dict[instruction]

    instruction_dict["desc"] = op_data.pop("desc")

    opcode = op_data.pop("opcode")
    opcode_dict = instruction_dict.setdefault(opcode, {})
    opcode_dict.update(op_data)

# pprint.pprint(data)

for category_id, category_data in sorted(data.items()):
    print
    print "    #### %s" % OP_CATEGORIES[category_id]
    print
    for instruction, instruction_data in sorted(category_data.items()):
        desc = instruction_data.pop("desc")
        if desc:
            print '    # %s - %s' % (instruction, desc)
        else:
            print '    # %s' % instruction
        print '    @opcode(('
        for opcode, op_data in sorted(instruction_data.items()):
            args = [
                "0x%x" % opcode,
                '"%s"' % op_data["mnemonic"],
                ADDRES_MODE_DICT[op_data["addr_mode"]],
            ]
            operant = op_data["operant"]
            if operant is not None:
#                 args.append("operant=%s # %s" % (
#                     operant, OPERANT_DICT[operant]
#                 ))
                args.append("operant=%s" % operant)

            print "        %s" % ", ".join(args)

        print "    ))"
        print "    def %s(self, op, ea=None, operant=None):" % instruction
#         if desc:
#             print '        """'
#             print '        %s' % desc
#             print '        """'
        print '        raise NotImplementedError("TODO: $%%x %s") %% op' % instruction
        print
