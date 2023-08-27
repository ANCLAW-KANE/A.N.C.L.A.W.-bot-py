from enum import Enum

Colors={
    'PURPLE_1' : '\x1b[38;5;99m'
}

class States_cook(Enum):
    NULL = ["-1", ""]
    START = ["0", " Вы кажется хотели сладкого"]
    ENTER_NAME = ["1", " Вы сказали что хотели сладкого но не указали сколько"]
    ENTER_WEIGHT = ["2", ""]
