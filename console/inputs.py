"""
    A set of classes that can be used to build interactive prompts
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

from console.output import FourBitConsoleColors, ConsoleTextStyle, color_text, reset_format


class ValidationError(Exception):
    """
        Represents some sort of error in the data the user entered

        :ivar message: The message to show the user
        :type message: str
    """

    def __init__(self, message):
        super(ValidationError, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class InputResult(Enum):
    """
        Represents the different outcomes of a prompt

        :cvar CONTINUE: Keep asking the user for input
        :type CONTINUE: int
        :cvar SUCCESS: The user has entered a valid value
        :type SUCCESS: int
        :cvar CANCEL: The user has cancelled the prompt
        :type CANCEL: int
        :cvar ERROR: The user has entered an invalid value and ``recurring`` is False
        :type ERROR: int
    """

    CONTINUE = 0
    SUCCESS = 1
    CANCEL = 2
    ERROR = 3


# Default Styles


DEFAULT_STYLES = {
    'prompt': ConsoleTextStyle(FourBitConsoleColors.BLUE, bold=True),
    'input': ConsoleTextStyle(FourBitConsoleColors.CYAN, bold=False),
    'error': ConsoleTextStyle(FourBitConsoleColors.RED, bold=True)
}

DEFAULT_SELECTION_STYLES = {
    'list': ConsoleTextStyle(FourBitConsoleColors.BLUE, bold=False)
}
DEFAULT_SELECTION_STYLES.update(DEFAULT_STYLES)

DEFAULT_LIST_STYLES = {
    'item-prompt': ConsoleTextStyle(FourBitConsoleColors.BLUE, bold=False),
    'item-input': ConsoleTextStyle(FourBitConsoleColors.CYAN, bold=False)
}
DEFAULT_LIST_STYLES.update(DEFAULT_STYLES)

# Default Error Messages


STRING_DEFAULT_ERRORS = {
    'too-long': "Must be at most {max} characters",
    'too-short': "Must be at least {min} characters",
    'empty': "Value cannot be empty",
    'not-equal': "Must have {amount} characters",
    'not-between': "Must be at least {min} and at most {max} characters"
}

NUMERIC_DEFAULT_ERRORS = {
    'overflow': "Number is too big",
    'too-big': "Must be less than or equal to {max}",
    'too-small': "Must be greater than or equal to {min}",
    'not-numeric': "Must be numeric",
    'not-whole': "Must be a whole number",
}
NUMERIC_DEFAULT_ERRORS.update(STRING_DEFAULT_ERRORS)

BOOLEAN_DEFAULT_ERRORS = {
    'invalid': "Invalid choice",
    'empty': "Please enter a value"
}

SELECTION_DEFAULT_ERRORS = {
    'invalid': "Invalid choice",
    'empty': "Please select an option"
}

LIST_DEFAULT_ERRORS = {
    'not-enough': "Not enough items",
}

FILE_DEFAULT_ERRORS = {
    'file-not-found': "Cannot find '{file_path}'",
    'file-exists': "'{file_path}' already exists",
    'perm-error': "Insufficient permissions to {mode}"
}


# Utilities

def in_range(in_num, minimum, maximum):
    """
        Sees if the entered value is within the given range

        :param in_num: The number to check
        :type in_num: float
        :param minimum: The minimum value of the range (inclusive)
        :type minimum: float
        :param maximum: The maximum value of the range (inclusive)
        :type maximum: float
        :returns: ``'lt'`` if less than, ``'gt'`` is greater than, and ``None`` if in
        :rtype: str
    """

    if minimum is not None and in_num < minimum:
        return 'lt'
    elif maximum is not None and in_num > maximum:
        return 'gt'
    else:
        return None


def default_list_format(index: int, in_str: object) -> str:
    """
        Makes the first character in the given string uppercase
        Also shows the position of the item in the list (1-based)

        :param index: The index of the item (0-based)
        :type index: int
        :param in_str: The string to format
        :type in_str: object
        :returns: The given string numbered and with the first character in uppercase
        :rtype: str
    """

    raw_str = str(in_str)
    return (str(index + 1) + '. ') + (raw_str[0].upper() + raw_str[1:])


def default_list_validation(raw_str: str, invalidate: callable):
    if len(raw_str) == 0:
        invalidate("Please enter a value")


# Input Options


@dataclass
class BaseInputOptions:
    """
        Represents options that apply to all inputs

        :ivar errors: The messages to show when the user enters invalid information
        :type errors: dict
        :ivar styles: The :py:class:`ConsoleTextStyle` to apply
        :type styles: dict
        :ivar suffix: A string that is put directly after the prompt
        :type suffix: str
        :ivar recurring: If the user makes an error, should we keep prompting them?
        :type recurring: bool
        :ivar cancel_codes: If the user enters any of these values, the input will be cancelled
        :type cancel_codes: tuple[str]
    """

    errors: dict = field(default_factory=dict)
    styles: dict = field(default_factory=lambda: DEFAULT_STYLES)
    suffix: str = ": "
    recurring: bool = True
    cancel_codes: tuple = ('!', '~')
    additional_validation: Callable[[str, Callable[[str], None]], None] = lambda raw_str, invalidate: None


@dataclass
class StringInputOptions(BaseInputOptions):
    """
        Represents options for a :py:class:`StringInput`

        :ivar minimum_length: The minimum length that the input has to be (inclusive)
        :type minimum_length: int
        :ivar maximum_length: The maximum length that the input can to be (inclusive)
        :type maximum_length: int
    """

    minimum_length: int = 1
    maximum_length: int = None
    errors: dict = field(default_factory=lambda: STRING_DEFAULT_ERRORS)


@dataclass
class NumericInputOptions(StringInputOptions):
    """
        Represents options for a :py:class:`NumericInput`

        :ivar minimum: The minimum value that can be entered
        :type minimum: float
        :ivar maximum: The maximum value that can be entered
        :type maximum: float
        :ivar allow_floats: Whether decimal-point numbers can be entered
        :type allow_floats: bool
    """

    minimum: float = None
    maximum: float = None
    allow_floats: bool = True
    errors: dict = field(default_factory=lambda: NUMERIC_DEFAULT_ERRORS)


@dataclass
class BooleanInputOptions(StringInputOptions):
    """
        Represents options for a :py:class:`BooleanInput`

        :ivar affirmative: The value the user needs to enter to say 'yes'
        :type affirmative: str
        :ivar negative: The value the user needs to enter to say 'no'
        :type negative: str
        :ivar hint_format: How the hint (ex: "({affirmative}/{negative})") will be displayed
        :type hint_format: str
    """

    affirmative: str = 'Y'
    negative: str = 'N'
    hint_format: str = ' ({affirmative}/{negative})'
    errors: dict = field(default_factory=lambda: BOOLEAN_DEFAULT_ERRORS)


@dataclass
class SelectionInputOptions(BaseInputOptions):
    """
        Represents options for a :py:class:`SelectionInput`

        :ivar item_formatter: A function that takes an item and formats it to display in the list, it gets the index of the item and the item itself and is expected to return a string
        :type item_formatter: callable[int, object] -> str
    """

    item_formatter: callable = field(default_factory=lambda: default_list_format)
    errors: dict = field(default_factory=lambda: SELECTION_DEFAULT_ERRORS)
    styles: dict = field(default_factory=lambda: DEFAULT_SELECTION_STYLES)


@dataclass
class ListInputOptions(BaseInputOptions):
    minimum_amount: int = 1
    maximum_amount: int = None
    validation_function: callable = field(default_factory=lambda: default_list_validation)
    item_format_string: str = "{current}/{maximum}"
    errors: dict = field(default_factory=lambda: LIST_DEFAULT_ERRORS)
    styles: dict = field(default_factory=lambda: DEFAULT_LIST_STYLES)
    stop_codes: tuple = field(default_factory=lambda: ('stop', 'done'))


@dataclass
class FileInputOptions(BaseInputOptions):
    errors: dict = field(default_factory=lambda: FILE_DEFAULT_ERRORS)
    require_exists: bool = True
    exists_ok: bool = False
    required_perms: int | None = None


# Inputs


class BaseInput:
    """
        Used as a base for all other input types

        :ivar options: the options for this input
    """

    option_class = BaseInputOptions

    def __init__(self, options=None, *args, **kwargs):
        """
            Initializes the input with the given options

            :param options: The options to apply to the input (will use default if None)
        """

        self.options = self.option_class() if options is None else options
        self._override_input = None
        self._override_print = None

    def __call__(self, prompt: str, *args, **kwargs):
        """
            Prompt the user with the given prompt, then get the result and the input back

            :param prompt: The prompt to ask the user
            :type prompt: str
            :returns: The result of the input (see :class InputResult:) and the value the user entered (or None is not applicable)
            :rtype: tuple[InputResult, object]
        """

        return self._invoke(prompt, *args, **kwargs)

    def _colored_input(self, prompt: str, prompt_style: ConsoleTextStyle, input_style: ConsoleTextStyle):
        entered = input(color_text(prompt, prompt_style) + color_text("", input_style, reset=False))
        reset_format()
        return entered

    def _show_prompt(self, prompt_string: str, prompt_style: ConsoleTextStyle, input_style: ConsoleTextStyle) -> str:
        prompt_string = prompt_string + self.options.suffix
        if self._override_input is None:
            return self._colored_input(prompt_string, prompt_style, input_style)
        else:
            return self._override_input(prompt_string)

    def _show_error(self, error_message: str) -> None:
        if self._override_print is None:
            print(color_text(error_message, self.options.styles.get('error')))
        else:
            self._override_print(error_message)

    def _invalidate(self, message_code: str, **kwargs) -> None:
        raise ValidationError(self.options.errors.get(message_code, "Unknown Error").format(**kwargs))

    def _invalidate_without_code(self, message: str) -> None:
        raise ValidationError(message)

    def _validate(self, raw_str: str) -> None:
        raise NotImplementedError(f"Validation not implemented for {self.__class__.__name__}")

    def _sanitize(self, raw_str: str) -> object:
        return raw_str

    def _main_loop(self, prompt: str, prompt_style: ConsoleTextStyle, input_style: ConsoleTextStyle, *args, **kwargs):
        raw_input = self._show_prompt(prompt, prompt_style, input_style)
        if raw_input in self.options.cancel_codes:
            return InputResult.CANCEL, None
        else:
            try:
                self._validate(raw_input)
                self.options.additional_validation(raw_input, self._invalidate_without_code)
                return InputResult.SUCCESS, self._sanitize(raw_input)
            except ValidationError as error:
                if self.options.recurring:
                    self._show_error(error.message)
                    return InputResult.CONTINUE, None
                else:
                    return InputResult.ERROR, None

    def _invoke(self, prompt: str, *args, **kwargs):
        output_code = None
        output = None
        while output_code is None or output_code == InputResult.CONTINUE:
            output_code, output = self._main_loop(prompt, self.options.styles['prompt'], self.options.styles['input'])
        return output_code, output

    def setup_testing(self, input_func: callable, print_func: callable) -> None:
        """
            Sets up this input for testing instead of production-use

            :param input_func: The function to run instead of input() when prompting the "user"
            :type input_func: callable[str] -> str
            :param print_func: The function to run instead of print() when outputting to the "user"
            :type print_func: callable[str] -> None
        """

        self._override_input = input_func
        self._override_print = print_func
        self.options.recurring = False


class StringInput(BaseInput):
    """
        Used to prompt the user for a string
    """

    option_class = StringInputOptions
    options: StringInputOptions = None

    def _validate(self, raw_str: str) -> None:
        string_length = len(raw_str)

        error = in_range(string_length, self.options.minimum_length, self.options.maximum_length)
        if error is not None:
            if self.options.minimum_length == self.options.maximum_length:
                self._invalidate('not-equal', amount=self.options.minimum_length)
            elif error == 'lt':
                self._invalidate('empty' if self.options.minimum_length == 1 else 'too-short',
                                 min=self.options.minimum_length)
            elif error == 'gt':
                self._invalidate('too-long', max=self.options.maximum_length)


class NumericInput(StringInput):
    """
        Used to prompt the user for a numerical value
    """

    option_class = NumericInputOptions
    options: NumericInputOptions = None

    def _sanitize(self, raw_str) -> object:
        return float(raw_str) if self.options.allow_floats else int(raw_str)

    def _validate(self, raw_str: str) -> None:
        super(NumericInput, self)._validate(raw_str)
        try:
            converted_value = float(raw_str)
            if self.options.allow_floats is False and converted_value % 1 != 0:
                self._invalidate('not-whole')
            else:
                error = in_range(converted_value, self.options.minimum, self.options.maximum)
                if error == 'gt':
                    self._invalidate('too-big', max=self.options.maximum)
                elif error == 'lt':
                    self._invalidate('too-small', min=self.options.minimum)
        except ValueError:
            self._invalidate('not-numeric')
        except OverflowError:
            if self.options.maximum is None:
                self._invalidate('overflow')
            else:
                self._invalidate('too-big', max=self.options.maximum)


class BooleanInput(StringInput):
    """
        Used to prompt the user for a boolean (usually a yes or no question)
    """

    option_class = BooleanInputOptions
    options: BooleanInputOptions = None

    def __init__(self, options: BooleanInputOptions, *args, **kwargs):
        options.errors.update({key: options.errors['invalid'] for key in options.errors.keys() if key != 'empty'})
        super(BooleanInput, self).__init__(options, *args, **kwargs)

    def _sanitize(self, raw_str) -> object:
        return True if raw_str.lower() == self.options.affirmative.lower() else False

    def _validate(self, raw_str: str) -> None:
        super(BooleanInput, self)._validate(raw_str)
        if raw_str.lower() != self.options.affirmative.lower() and raw_str.lower() != self.options.negative.lower():
            self._invalidate('invalid')

    def _invoke(self, prompt: str, *args, **kwargs):
        prompt += self.options.hint_format.format(affirmative=self.options.affirmative, negative=self.options.negative)
        return super(BooleanInput, self)._invoke(prompt)


class ListInput(BaseInput):
    """
        Used to prompt the user for a series of items
    """

    option_class = ListInputOptions
    options: ListInputOptions = None

    def list_invalidate(self, message):
        raise ValidationError(message)

    def _validate(self, raw_str: str) -> None:
        self.options.validation_function(raw_str, self.list_invalidate)

    def __call__(self, prompt: str, *args, **kwargs):
        return self._invoke(prompt)

    def _invoke(self, prompt: str, *args, **kwargs):
        if self._override_print is None:
            print(color_text(prompt + self.options.suffix, self.options.styles['prompt']))
        else:
            self._override_print(prompt + self.options.suffix)
        output_list = []
        output_code = None
        while output_code is None:
            item_prompt = self.options.item_format_string.format(current=len(output_list) + 1,
                                                                 maximum='∞' if self.options.maximum_amount is None else self.options.maximum_amount)
            item_code, item = self._main_loop(item_prompt, self.options.styles['item-prompt'],
                                              self.options.styles['item-input'])
            if item_code == InputResult.SUCCESS:
                if item.lower() in self.options.stop_codes:
                    if len(output_list) < self.options.minimum_amount:
                        self._show_error(self.options.errors.get('not-enough', "Unknown Error"))
                    else:
                        output_code = InputResult.SUCCESS
                else:
                    output_list.append(item)
                if len(output_list) == self.options.maximum_amount:
                    output_code = InputResult.SUCCESS
            elif item_code == InputResult.CANCEL:
                output_code = InputResult.CANCEL
        return output_code, output_list


class SelectionInput(BaseInput):
    """
        Used to have the user select from a list of values
    """

    option_class = SelectionInputOptions
    options: SelectionInputOptions = None

    def __init__(self, options, *args, **kwargs):
        """
            Initializes the input with the given options

            :param options: The options to apply to the input (will use default if None)
        """

        super(SelectionInput, self).__init__(options, *args, **kwargs)
        self._test_mode = False

    def __call__(self, prompt: str, choices: list[object], *args, **kwargs):
        """
            Prompt the user with the given prompt, then get the result and the input back

            :param prompt: The prompt to ask the user
            :type prompt: str
            :param choices: The list the user can select from
            :type choices: list[object]
            :returns: The result of the input (see :class InputResult:) and the value the user entered (or None is not applicable)
            :rtype: tuple[InputResult, object] 
        """

        return self._invoke(prompt, choices, *args, **kwargs)

    def _validate(self, raw_str: str) -> None:
        pass

    def _show_list(self, items: list[object]) -> str:
        output_string = '\n'.join([self.options.item_formatter(index, item) for index, item in enumerate(items)])
        if self._override_print is None:
            print(color_text(output_string, self.options.styles.get('list')))
        else:
            return self._override_print(output_string)

    def _generate_numeric_options(self, list_length: int):
        errors = {key: SELECTION_DEFAULT_ERRORS['invalid'] for key in NUMERIC_DEFAULT_ERRORS if key != 'empty'}
        errors['empty'] = self.options.errors['empty']
        return NumericInputOptions(allow_floats=False, minimum=1, maximum=list_length, errors=errors,
                                   suffix=self.options.suffix, cancel_codes=self.options.cancel_codes,
                                   styles=self.options.styles)

    def _invoke(self, prompt: str, choices: list[object], *args, **kwargs):
        numeric_options = self._generate_numeric_options(len(choices))
        numeric_input = NumericInput(numeric_options)
        if self._test_mode:
            numeric_input.setup_testing(self._override_input, self._override_print)
        self._show_list(choices)
        selection: int
        result, selection = numeric_input(prompt)
        return result, None if selection is None else (selection - 1)

    def setup_testing(self, input_func: callable, print_func: callable):
        super().setup_testing(input_func, print_func)
        self._test_mode = True


class FileInput(BaseInput):
    """
        Used to have the user select a file
    """

    options: FileInputOptions
    option_class = FileInputOptions

    PERM_ERRS = ['exists', 'execute', 'write', '', 'read']

    def _validate(self, raw_str: str) -> None:
        p = Path(raw_str)
        if self.options.require_exists and p.exists() is False:
            self._invalidate('file-not-found', file_path=str(p.as_posix()))
        if self.options.exists_ok is False and p.exists() is True:
            self._invalidate('file-exists', file_path=str(p.as_posix()))
        if self.options.required_perms is not None:
            if self.options.required_perms == os.W_OK and p.exists() is False and os.access(p.parent, os.W_OK) is False:
                self._invalidate('perm-error', mode=self.PERM_ERRS[self.options.required_perms])
            elif self.options.required_perms != os.W_OK and os.access(p, self.options.required_perms) is False:
                self._invalidate("perm-error", mode=self.PERM_ERRS[self.options.required_perms])

    def _invoke(self, prompt: str, *args, **kwargs) -> tuple[InputResult, Path | None]:
        results = list(super(FileInput, self)._invoke(prompt, *args, **kwargs))
        results[1] = Path(results[1])
        return tuple(results)


TYPE_MAPPINGS = {
    'str': StringInput(StringInputOptions()),
    'int': NumericInput(NumericInputOptions(allow_floats=False)),
    'float': NumericInput(NumericInputOptions()),
    'bool': BooleanInput(BooleanInputOptions()),
    'Path': FileInput(FileInputOptions(require_exists=True, exists_ok=True, required_perms=os.R_OK))
}
