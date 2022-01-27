from dataclasses import dataclass, field
from enum import Enum

from console.output import ConsoleColors, ConsoleTextStyle, color_text


class ValidationError(Exception):

    def __init__(self, message):
        super(ValidationError, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class InputResult(Enum):
    CONTINUE = 0
    SUCCESS = 1
    CANCEL = 2
    ERROR = 3


# Default Styles


DEFAULT_STYLES = {
    'prompt': ConsoleTextStyle(ConsoleColors.BLUE, True, False),
    'error': ConsoleTextStyle(ConsoleColors.RED, True, False)
}

DEFAULT_SELECTION_STYLES = {
    'list': ConsoleTextStyle(ConsoleColors.BLUE, False, False)
}
DEFAULT_SELECTION_STYLES.update(DEFAULT_STYLES)

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


# Utilities

def in_range(in_num, minimum, maximum):
    if minimum is not None and in_num < minimum:
        return 'lt'
    elif maximum is not None and in_num > maximum:
        return 'gt'
    else:
        return None


def first_upper(index, in_str):
    raw_str = str(in_str)
    return (str(index + 1) + '. ') + (raw_str[0].upper() + raw_str[1:])


# Input Options


@dataclass
class BaseInputOptions:
    errors: dict = field(default_factory=dict)
    styles: dict = field(default_factory=lambda: DEFAULT_STYLES)
    suffix: str = ": "
    recurring: bool = True
    cancel_codes: tuple = ('!', '~')


@dataclass
class StringInputOptions(BaseInputOptions):
    minimum_length: int = 1
    maximum_length: int = None
    errors: dict = field(default_factory=lambda: STRING_DEFAULT_ERRORS)


@dataclass
class NumericInputOptions(StringInputOptions):
    minimum: float = None
    maximum: float = None
    allow_floats: bool = True
    errors: dict = field(default_factory=lambda: NUMERIC_DEFAULT_ERRORS)


@dataclass
class BooleanInputOptions(StringInputOptions):
    affirmative: str = 'Y'
    negative: str = 'N'
    hint_format: str = ' ({affirmative}/{negative})'
    errors: dict = field(default_factory=lambda:  BOOLEAN_DEFAULT_ERRORS)


@dataclass
class SelectionInputOptions(BaseInputOptions):
    item_formatter: callable = field(default_factory=lambda:  first_upper)
    errors: dict = field(default_factory=lambda:  SELECTION_DEFAULT_ERRORS)
    styles: dict = field(default_factory=lambda: DEFAULT_SELECTION_STYLES)

# Inputs


class BaseInput:
    option_class = BaseInputOptions

    def __init__(self, options=None):
        self.options = self.option_class() if options is None else options
        self._override_input = None
        self._override_print = None

    def __call__(self, prompt: str) -> tuple[InputResult, object]:
        return self._invoke(prompt)

    def _show_prompt(self, prompt_string: str) -> str:
        prompt_string = prompt_string + self.options.suffix
        if self._override_input is None:
            return input(color_text(prompt_string, self.options.styles.get('prompt')))
        else:
            return self._override_input(prompt_string)

    def _show_error(self, error_message: str) -> str:
        if self._override_print is None:
            print(color_text(error_message, self.options.styles.get('error')))
        else:
            self._override_print(error_message)

    def _invalidate(self, message_code, **kwargs):
        raise ValidationError(self.options.errors.get(message_code, "Unknown Error").format(**kwargs))

    def _validate(self, raw_str: str) -> None:
        raise NotImplementedError(f"Validation not implemented for {self.__class__.__name__}")

    def _sanitize(self, raw_str) -> object:
        return raw_str

    def _main_loop(self, prompt: str):
        raw_input = self._show_prompt(prompt)
        if raw_input in self.options.cancel_codes:
            return InputResult.CANCEL, None
        else:
            try:
                self._validate(raw_input)
                return InputResult.SUCCESS, self._sanitize(raw_input)
            except ValidationError as error:
                if self.options.recurring:
                    self._show_error(error.message)
                    return InputResult.CONTINUE, None
                else:
                    return InputResult.ERROR, None

    def _invoke(self, prompt: str):
        output_code = None
        output = None
        while output_code is None or output_code == InputResult.CONTINUE:
            output_code, output = self._main_loop(prompt)
        return output_code, output

    def setup_testing(self, input_func: callable, print_func: callable):
        self._override_input = input_func
        self._override_print = print_func
        self.options.recurring = False


class StringInput(BaseInput):
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
    option_class = BooleanInputOptions
    options: BooleanInputOptions = None

    def __init__(self, options: BooleanInputOptions):
        options.errors.update({key: options.errors['invalid'] for key in options.errors.keys() if key != 'empty'})
        super(BooleanInput, self).__init__(options)

    def _sanitize(self, raw_str) -> object:
        return True if raw_str.lower() == self.options.affirmative.lower() else False

    def _validate(self, raw_str: str) -> None:
        super(BooleanInput, self)._validate(raw_str)
        if raw_str.lower() != self.options.affirmative.lower() and raw_str.lower() != self.options.negative.lower():
            self._invalidate('invalid')

    def _invoke(self, prompt: str):
        prompt += self.options.hint_format.format(affirmative=self.options.affirmative, negative=self.options.negative)
        return super(BooleanInput, self)._invoke(prompt)


class SelectionInput:
    option_class = SelectionInputOptions
    options: SelectionInputOptions = None

    def __init__(self, options):
        self.options = self.option_class() if options is None else options
        self._override_input = None
        self._override_print = None
        self._test_mode = False

    def __call__(self, prompt: str, choices: list[object]):
        return self._invoke(prompt, choices)

    def _show_list(self, items: list[object]) -> str:
        output_string = '\n'.join([self.options.item_formatter(index, item) for index, item in enumerate(items)])
        if self._override_print is None:
            return print(color_text(output_string, self.options.styles.get('list')))
        else:
            return self._override_input(output_string)

    def _generate_numeric_options(self, list_length: int):
        errors = {key: SELECTION_DEFAULT_ERRORS['invalid'] for key in NUMERIC_DEFAULT_ERRORS if key != 'empty'}
        errors['empty'] = self.options.errors['empty']
        return NumericInputOptions(allow_floats=False, minimum=1, maximum=list_length, errors=errors,
                                   suffix=self.options.suffix, cancel_codes=self.options.cancel_codes,
                                   styles=self.options.styles)

    def _invoke(self, prompt: str, choices: list[object]):
        numeric_options = self._generate_numeric_options(len(choices))
        numeric_input = NumericInput(numeric_options)
        if self._test_mode:
            numeric_input.setup_testing(self._override_input, self._override_print)
        self._show_list(choices)
        result, selection = numeric_input(prompt)
        return result, selection - 1

    def setup_testing(self, input_func: callable, print_func: callable):
        self._override_input = input_func
        self._override_print = print_func
        self.options.recurring = False
        self._test_mode = True
