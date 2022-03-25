from dataclasses import dataclass
from inspect import signature, Parameter
from typing import Callable

from inputs import BaseInputOptions, InputResult, OPTIONS_MAPPINGS, BaseInput, TYPE_MAPPINGS


@dataclass
class FormField:
    name: str
    message: str
    options: BaseInputOptions
    choices: list[object] = None
    optional: bool = False
    default: object = None
    _prompt: BaseInput = None

    def prompt(self, *args, **kwargs):
        return self._prompt(*args, **kwargs)

    def set_prompt(self, new_prompt: BaseInput):
        self._prompt = new_prompt


class FormMeta(type):

    def __new__(mcs, name, bases, namespace, *args, **kwargs):

        namespace['__fields'] = []

        for name, field in [t for t in namespace.items() if issubclass(FormField, type(t[1]))]:
            prompt = OPTIONS_MAPPINGS[type(field.options)](field.options)
            field.set_prompt(prompt)
            namespace['__fields'].append(field)

        return super().__new__(mcs, name, bases, namespace)


DEFAULT_IGNORE_PARAMS = ('self', 'cls', 'mcs', 'args', 'kwargs')


class Form(metaclass=FormMeta):

    __fields: list[FormField] = []

    def __init__(self, override_fields: list[FormField] = None):
        if override_fields is not None:
            self.__fields = override_fields

    @classmethod
    def from_function(cls, func: Callable, prompts: dict[str, str], ignore_params: tuple[str] = DEFAULT_IGNORE_PARAMS, type_map: dict[str, BaseInput] = TYPE_MAPPINGS):
        fields = []
        for param in signature(func).parameters.values():
            if param.name not in ignore_params and param.kind == Parameter.POSITIONAL_OR_KEYWORD:
                if param.annotation in type_map.keys():
                    prompt = type_map[param.annotation]
                    field = FormField(name=param.name, message=prompts.get(param.name, param.name),
                                      options=BaseInputOptions(), optional=param.default != Parameter.empty,
                                      default=param.default)
                    field.set_prompt(prompt)
                    fields.append(field)
                else:
                    raise TypeError(f"{param.annotation} is not supported, specify it in type_map")
        return Form(override_fields=fields)

    def _invoke(self) -> tuple[InputResult, dict[str, object]]:
        data: dict[str, object] = {}
        form_result: InputResult = InputResult.SUCCESS
        for field in self.__fields:
            args = [field.message] if field.choices is None else [field.message, field.choices]
            result, output = field.prompt(*args)
            if result == InputResult.CANCEL:
                if field.optional:
                    data[field.name] = field.default
                else:
                    form_result = InputResult.CANCEL
                    break
            elif result == InputResult.SUCCESS:
                data[field.name] = output
        return form_result, data

    def __call__(self) -> tuple[InputResult, dict[str, object]]:
        return self._invoke()
