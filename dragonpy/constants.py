CLI_EPILOG = 'Project Homepage: https://github.com/jedie/DragonPy'

DRAGON32 = "Dragon32"
DRAGON64 = "Dragon64"
COCO2B = "CoCo2b"
SBC09 = "sbc09"
SIMPLE6809 = "Simple6809"
MULTICOMP6809 = "Multicomp6809"
VECTREX = "Vectrex"

VERBOSITY_DICT = {
    1: "hardcode DEBUG ;)",
    10: "DEBUG",
    20: "INFO",
    30: "WARNING",
    40: "ERROR",
    50: "CRITICAL/FATAL",
    99: "nearly all off",
    100: "all off",
}
VERBOSITY_DEFAULT_VALUE = 100
VERBOSITY_DICT2 = {}
VERBOSITY_STRINGS = []
VERBOSITY_DEFAULT = None

for no, text in sorted(VERBOSITY_DICT.items()):
    text = f"{no:3d}: {text}"
    if no == VERBOSITY_DEFAULT_VALUE:
        VERBOSITY_DEFAULT = text
    VERBOSITY_STRINGS.append(text)
    VERBOSITY_DICT2[text] = no

# print(VERBOSITY_STRINGS)
# print(VERBOSITY_DICT2)
# print(VERBOSITY_DEFAULT_VALUE, VERBOSITY_DEFAULT)

assert VERBOSITY_DEFAULT is not None
assert VERBOSITY_DICT2[VERBOSITY_DEFAULT] == VERBOSITY_DEFAULT_VALUE
