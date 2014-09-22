

from dragonpy.components.MC6809data.MC6809_data import OP_DATA


def get_opdata():
    opdata = {}
    for instr_data in list(OP_DATA.values()):
        for mnemonic, mnemonic_data in list(instr_data["mnemonic"].items()):
            for op_code, op_data in list(mnemonic_data["ops"].items()):
                op_data["mnemonic"] = mnemonic
                op_data["needs_ea"] = mnemonic_data["needs_ea"]
                for key in ("read_from_memory", "write_to_memory", "register"):
                    op_data[key] = mnemonic_data[key]
                opdata[op_code] = op_data
    return opdata

MC6809OP_DATA_DICT = get_opdata()
