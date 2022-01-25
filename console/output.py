"""
    A set of functions that are helpful when output data
"""
import sys
from dataclasses import dataclass

__all__ = [
    'ConsoleColors',
    'ConsoleTextStyle',
    'color_text',
    'progressbar'
]


class ConsoleColors:
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    PURPLE = 5
    CYAN = 6
    WHITE = 7


@dataclass
class ConsoleTextStyle:
    color: int
    bold: bool
    high_intensity: bool


def color_text(in_str: str, style: ConsoleTextStyle):
    return f"\033[{1 if style.bold else 0};{9 if style.high_intensity else 3}{style.color}m" + in_str + "\033[0m"


def progressbar(it, prefix="", size=60):
    count = len(it)

    def show(j):
        x = int(size*j/count)
        sys.stdout.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        sys.stdout.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    sys.stdout.write("\n")
    sys.stdout.flush()



