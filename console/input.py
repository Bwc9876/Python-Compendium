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

LIST_SELECTION_ERROR_MESSAGES = {
    'invalid': "Invalid choice"
}

__all__ = [
    'string_input',
    'numeric_input',
    'list_selection_input'
]


def empty(in_str, strip=True):
    return len((in_str.strip() if strip else in_str)) == 0


def string_input(prompt, recurring=False, strip=True, errors=None):
    if errors is None:
        errors = STRING_INPUT_ERROR_MESSAGES
    output_string = None
    done = False
    while not done:
        raw_string = input(prompt)
        if empty(raw_string, strip=strip):
            if recurring:
                print(errors['empty'])
            else:
                done = True
        else:
            output_string = raw_string
            done = True
    return output_string


def numeric_input(prompt, minimum=None, maximum=None, allow_floats=True, recurring=False, strip=True, errors=None):
    if errors is None:
        errors = NUMERIC_INPUT_ERROR_MESSAGES
    output_number = None
    done = False
    while recurring and not done:
        raw_string = input(prompt)
        if empty(raw_string, strip=strip):
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


def list_selection_input(prompt, items, errors=None, item_format_method=lambda x: str(x)):
    if errors is None:
        errors = LIST_SELECTION_ERROR_MESSAGES
    numeric_error_dict = {key: errors['invalid'] for key in NUMERIC_INPUT_ERROR_MESSAGES.keys()}
    list_string = '\n'.join([f"{i + 1}: {item_format_method(item)}" for i, item in enumerate(items)])
    print(list_string)
    choice = int(numeric_input(prompt, minimum=1, maximum=len(items), allow_floats=False, recurring=True, strip=True, errors=numeric_error_dict))
    return items[choice - 1]














