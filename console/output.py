"""
    A set of functions that are helpful when outputting data
"""

import sys
from enum import Enum
from dataclasses import dataclass


class ConsoleColorMode(Enum):
    FOUR_BIT = 0
    EIGHT_BIT = 1
    RGB = 2

COLOR_MODE = ConsoleColorMode.EIGHT_BIT


class ConsoleColors(Enum):
    """
        Use this static class to select colors in :class:ConsoleTextStyle
    """

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
    """
        A set of options for outputting colored and bolded text to the console

        :ivar color: The color of the text (see :class:ConsoleColors)
        :type color: int
        :ivar bold: Whether the text will be bolded in the console
        :type bold: bool
        :ivar high_intesity: Switch to the high intensity variant of the color selected
        :type high_itensity: bool
    """

    fg_color: int|tuple[int]
    bg_color: int|tuple[int]
    bold: bool = False
    underline: bool = False
    overline: bool = False
    invert: bool = False
    blink: bool = False
    high_intensity = False

    def get_flags(self):
        return (self.bold, self.underline, self.overline, self.invert, self.blink)


flag_codes = (
    (1, None),
    (4, 24),
    (53, 55),
    (7, 27),
    (5, 25),
)

# \033[color;bg;flagsmMESSAGE\033[0m


def handle_flags(style):
    flags = style.get_flags()
    flag_String = ""
    for flag, possible in enumerate(flag_codes):
        if flags[flag] is True and possible[0] is not None:
            flag_string += f"{possible[0]};"
        elif flags[flag] is False and possible[1] is not None:
            flag_string += f"{possible[1]};"
    return flag_string
            
def handle_color(color_type, style, mode):
    color = style.fg_Color if color_type == 0 else style.bg_color
    if style.color is None:
        return ""
    else:
        if mode == ConsoleColorMode.RGB:
            return str(38 id color_type == 0 else 48) + f";2;{color[0]};{color[1]};{color[2]};"

def color_text(in_str: str, style: ConsoleTextStyle, reset=True, override_color_mode=None):
    """
        Colors the given string according to the provided :class:ConsoleTextStyle

        :param in_str: The string to color
        :type in_str: str
        :param style: The style to apply
        :type style: ConsoleTextStyle
    """
    if style is None:
        return in_str
    else:
        if override_color_mode is None:
            color_mode = COLOR_MODE
        else:
            color_mode = override_color_mode
        command_sequence = "\033["



def progressbar(it, prefix="", size=60):
    """
        Wraps a given iterator or generator (use a cast to list) to print a progress bar to the console

        :param it: The iterator to apply the bar to
        :type it: iterable
        :param prefix: Characters to show before the bar
        :type prefix: str
        :param size: The size of the bar
        :type size: int
    """

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



