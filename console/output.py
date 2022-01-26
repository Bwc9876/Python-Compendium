"""
    A set of functions that are helpful when outputting data
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

    color: int
    bold: bool
    high_intensity: bool


def color_text(in_str: str, style: ConsoleTextStyle):
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
        return f"\033[{1 if style.bold else 0};{9 if style.high_intensity else 3}{style.color}m" + in_str + "\033[0m"


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



