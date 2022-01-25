"""
    A set of functions that are helpful when accepting user input
"""

STRING_INPUT_ERROR_MESSAGES = {
    'empty': "Please enter a value"
}

NUMERIC_INPUT_ERROR_MESSAGES = {
    'empty': "Please enter a value",
    'overflow': "Value is too big",
    'non-numeric': "Must be a number",
    'min-max': "Please enter a number between {minimum} and {maximum}",
    'whole': "Must be a whole number"
}

SELECTION_INPUT_ERROR_MESSAGES = {
    'invalid': "Invalid choice"
}

BOOL_INPUT_ERROR_MESSAGES = {
    'empty': "Please enter a value",
    'invalid': "Invalid choice"
}

LIST_INPUT_ERROR_MESSAGES = {
    'invalid': "Invalid value",
    'duplicate': "Value already entered"
}

__all__ = [
    'string_input',
    'numeric_input',
    'selection_input',
    'list_input',
    'bool_input'
]


def empty(in_str: str, strip: bool=True) -> bool:
    """
        Returns if the given string is empty, with or without stripping it

        :param in_str: The string to check
        :type in_str: str
        :param strip: Whether to strip the string before checking
        :type strip: bool
        :returns: Whether the string is empty
        :rtype: bool
    """

    return len((in_str.strip() if strip else in_str)) == 0


def string_input(prompt: str, recurring: bool=True, errors: dict=None) -> str:
    """
        Asks the user for a non-empty string and then returns it

        :param prompt: The prompt to ask the user
        :type prompt: str
        :param recurring: If the user enters an incorrect value, should the program keep asking them?
        :type recurring: bool
        :param errors: The error messages to display under different conditions
        :type errors: dict
        :returns: The string the user inputted, or None if recurring is False
        :rtype: str
    """

    if errors is None:
        errors = STRING_INPUT_ERROR_MESSAGES
    output_string = None
    done = False
    while not done:
        raw_string = input(prompt)
        if empty(raw_string, strip=True):
            if recurring:
                print(errors['empty'])
            else:
                done = True
        else:
            output_string = raw_string
            done = True
    return output_string


def numeric_input(prompt, minimum=None, maximum=None, allow_floats=True, recurring=True, errors=None):
    """
        Asks the user for a numerical value and returns it

        :param prompt: The prompt to ask the user
        :type prompt: str
        :param minimum: The minimum number (inclusive) that can be entered
        :type minimum: float
        :param maximum: The maximum number (inclusive) that can be entered
        :type maximum: float
        :param allow_floats: Whether to allow floating-point numbers (decimals) to be entered
        :type allow_floats: bool
        :param recurring: If the user enters an incorrect value, should the program keep asking them?
        :type recurring: bool
        :param errors: The error messages to display under different conditions
        :type errors: dict
        :param errors: 
        :returns: The number the user entered
        :rtype: float
    """

    if errors is None:
        errors = NUMERIC_INPUT_ERROR_MESSAGES
    output_number = None
    done = False
    while not done:
        raw_string = input(prompt)
        if empty(raw_string, strip=True):
            if recurring:
                print(errors['empty'])
            else:
                done = True
        else:
            try:
                converted_number = float(raw_string)
                if minimum <= converted_number <= maximum:
                    if allow_floats is False and converted_number % 1 != 0:
                        print(errors['whole'])
                    else:
                        output_number = converted_number
                        done = True
                else:
                    if recurring:
                        print(errors['min-max'].format(minimum=minimum, maximum=maximum))
                    else:
                        done = True
            except ValueError:
                if recurring:
                    print(errors['non-numeric'])
                else:
                    done = True
            except OverflowError:
                if recurring:
                    print(errors['overflow'])
                else:
                    done = True
    return output_number


def selection_input(prompt, items, errors=None, item_format_method=lambda x: str(x)):
    """
        Prompts the user with a list of items and returns which one they selected

        :param prompt: The prompt to ask the user
        :type prompt: str
        :param items: The list of items the user can chose from
        :type items: list[Any]
        :param recurring: If the user enters an incorrect value, should the program keep asking them?
        :type recurring: bool
        :param errors: The error messages to display under different conditions
        :type errors: dict
        :param item_format_method: A function to run on each list item before printing it
        :type item_format_method: callable[str] -> str
        :returns: The item the user selected
        :rtype: Any
    """

    if errors is None:
        errors = SELECTION_INPUT_ERROR_MESSAGES
    numeric_error_dict = {key: errors['invalid'] for key in NUMERIC_INPUT_ERROR_MESSAGES.keys()}
    list_string = '\n'.join([f"{i + 1}: {item_format_method(item)}" for i, item in enumerate(items)])
    print(list_string)
    choice = int(numeric_input(prompt, minimum=1, maximum=len(items), allow_floats=False, recurring=True, strip=True, errors=numeric_error_dict))
    return items[choice - 1]

def list_input(prompt, prefix='{current}/{maximum}> ', validation_method=lambda x: empty(x, strip=True) is False, max_amount=-1, stop_codes=('stop', 'exit'), allow_duplicates=True, errors=None):
    """
        Asks the user for a limited or unlimited list of items

        :param prompt: The prompt to initially ask the user
        :type prompt: str
        :param prefix: The string to show for each item the user will enter
        :type prefix: str
        :param validation_method: The function to run on an entered item to see if it's valid
        :type validation_method: callable[str] -> bool
        :param max_amount: The max amount of items that can be entered (-1 for infinite)
        :type max_amount: int
        :param stop_codes: If any of these values are entered, stop accepting input and return the list as-is
        :type stop_codes: list[str]
        :param errors: The error messages to display under different conditions
        :type errors: dict
        :param allow_dulicates: Whether to allow the user to enter a value more than once
        :type allow_duplicates: bool
        :returns: A list of the values the user entered
        :rtype: list[str]
    """

    if errors is None:
        errors = LIST_INPUT_ERROR_MESSAGES
    output_list = []
    done = False
    print(prompt)
    while not done:
        raw_input = input(prefix.format(current=len(output_list) + 1, maximum=(max_amount if max_amount > 0 else '∞')))
        if raw_input.lower() in stop_codes:
            done = True
        else:
            if validation_method(raw_input):
                if allow_duplicates is False and raw_input in output_list:
                  print(errors['duplicate'])
                else:
                  output_list.append(raw_input)
                  if len(output_list) == max_amount:
                      done = True
            else:
                print(errors['invalid'])
    return output_list


def bool_input(prompt, yes=('y', 'yes'), no=('n', 'no'), recurring=True, errors=None, fallback_to=None):
    """
        Asks the user a yes-no question

        :param prompt: The prompt to ask the user
        :type prompt: str
        :param yes: Affirmative values
        :type yes: tuple[str]
        :param no: Negative values
        :type no: tuple[str]
        :param recurring: If the user enters an incorrect value, should the program keep asking them?
        :type recurring: bool
        :param errors: The error messages to display under different conditions
        :type errors: dict
        :param fallback_to: If the value entered is not in yes or no, what value should we fall back to (unless recurring is True)
        :type fallback_to: bool
        :returns: The boolean representation of what the user entered
        :rtype: bool
    """

    if errors is None:
        errors = BOOL_INPUT_ERROR_MESSAGES
    output_bool = None
    done = False
    while not done:
        raw_string = input(prompt).lower()
        if empty(raw_string, strip=True):
            if recurring:
                print(errors['empty'])
            else:
                done = True
        else:
            if raw_string in yes:
                done = True
                output_bool = True
            elif raw_string in no:
                done = True
                output_bool = False
            else:
                if fallback_to is None:
                    if recurring:
                        print(errors['invalid'])
                    else:
                        done = True
                else:
                    output_bool = fallback_to
                    done = True
    return output_bool
