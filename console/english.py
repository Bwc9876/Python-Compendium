
VOWELS = ('a', 'e', 'i', 'o', 'u', 'y')
TRUE_VOWELS = tuple(VOWELS[:-1])

ARTICLES = ('a', 'an', 'the')
COORD_CONJUNCTIONS = ('for', 'and', 'nor', 'but', 'or', 'yet')

__all__ = [
    "pluralize",
    "auto_plural",
    "number_of",
    "list_items",
    "a_or_an",
    "cap_first",
    "cap_first_title",
    "cap_first_all",
    "title"
]

def pluralize(word: str, plural_string="s", vowel_plural_string="es", y_plural_string="ies"):
    if word[-1].lower() in VOWELS:
        if word[-1].lower() == 'y':
            return word[:-1] + y_plural_string
        else:
            return word + vowel_plural_string
    else:
        return word + plural_string


def auto_plural(word: str, num: int):
    if num > 1:
        return pluralize(word)
    else:
        return word


def number_of(items: list, name: str):
    return len(items) + " " + (auto_plural(name, len(items)))


def list_items(items: list):
    if len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return str(items[0]) + " and " + str(items[1])
    else:
        string_list = [str(item) for item in items]
        string_list[-1] = "and " + string_list[-1]
        return ', '.join(string_list)    


def a_or_an(word: str, consider_acronyms=False):
    if word[0] in TRUE_VOWELS and (consider_acronyms is False or word.isupper() is False):
        return "an " + word
    return "a " + word


def cap_first(word: str):
    return word[0].upper() + word[1:]


def cap_first_title(word: str):
    if word.lower() in ARTICLES or word.lower() in COORD_CONJUNCTIONS or len(word) < 4:
        return cap_first(word)
    else:
        return word


def cap_first_all(phrase: str):
    return ' '.join([cap_first(word) for word in phrase.split(" ")])


def title(phrase: str):
    return ' '.join([cap_first_title(word.lower()) for word in phrase.split(" ")])



