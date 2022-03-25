from abc import ABC, abstractmethod
from enum import IntEnum
from os import PathLike

from console.output import ConsoleTextStyle, color_text, FourBitConsoleColors


class LogType(IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class LogDestination(ABC):

    @staticmethod
    def _format_message(message: str, log_type: LogType, tags: list[str]) -> str:
        return f"({log_type.name.upper()}){''.join([f'[{tag}]' for tag in tags])}: {message}"


    @abstractmethod
    def write(self, log_type: LogType, message: str, tags: list[str], end: str = '\n'):
        pass


class ConsoleLog(LogDestination):

    DEFAULT_STYLES = {
        LogType.DEBUG: ConsoleTextStyle(fg_color=FourBitConsoleColors.CYAN),
        LogType.INFO: ConsoleTextStyle(fg_color=FourBitConsoleColors.BLUE),
        LogType.WARNING: ConsoleTextStyle(fg_color=FourBitConsoleColors.YELLOW),
        LogType.ERROR: ConsoleTextStyle(fg_color=FourBitConsoleColors.RED),
        LogType.CRITICAL: ConsoleTextStyle(fg_color=FourBitConsoleColors.RED, bold=True)
    }

    def __init__(self, styles: dict[str, ConsoleTextStyle]):
        self.styles = self.DEFAULT_STYLES.copy()
        self.styles.update(styles)

    def write(self, log_type: LogType, message: str, tags: list[str], end: str = '\n') -> None:
        formatted = self._format_message(message, log_type, tags)
        print(color_text(formatted, self.styles[log_type]), end=end)


class FileLog(LogDestination):

    def __init__(self, file: PathLike):
        self.file = file

    def write(self, log_type: LogType, message: str, tags: list[str], end: str = '\n') -> None:
        formatted = self._format_message(message, log_type, tags)
        with open(self.file, mode='w+', encoding='utf-8') as file:
            file.writelines([formatted])


class Logger:

    def __init__(self, key: str, destinations: dict[LogType, tuple[LogDestination]]):
        self.key = key
        self.destinations = destinations

    def log(self, message: str, log_type: LogType, tags: list[str]) -> None:
        for dest in self.destinations[log_type]:
            dest.write(log_type, message, tags)

    def log_debug(self, message: str, tags: list[str]) -> None:
        self.log(message, LogType.DEBUG, tags)

    def log_info(self, message: str, tags: list[str]) -> None:
        self.log(message, LogType.INFO, tags)

    def log_warning(self, message: str, tags: list[str]) -> None:
        self.log(message, LogType.WARNING, tags)

    def log_error(self, message: str, tags: list[str]) -> None:
        self.log(message, LogType.ERROR, tags)

    def log_critical(self, message: str, tags: list[str]) -> None:
        self.log(message, LogType.CRITICAL, tags)


class LogManager:

    __loggers: dict[str, Logger] = {}

    DEFAULT_CONSOLE_LOG = ConsoleLog({})

    DEFAULT_DESTINATIONS = {t: DEFAULT_CONSOLE_LOG for t in LogType}

    def __new__(cls, *args, **kwargs):
        raise TypeError("LogManager Is Static")

    @classmethod
    def request_logger(cls, name: str, destinations=None) -> Logger:
        if destinations is None:
            destinations = cls.DEFAULT_DESTINATIONS
        if name in cls.__loggers.keys():
            return cls.__loggers[name]
        else:
            new_logger = Logger(name, destinations)
            cls.__loggers[name] = new_logger
            return new_logger

    @classmethod
    def unregister_logger(cls, name: str) -> None:
        cls.__loggers.pop(name)

    @classmethod
    def clear_all_loggers(cls) -> None:
        cls.__loggers.clear()


