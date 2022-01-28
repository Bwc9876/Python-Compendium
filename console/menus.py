"""
    A set of classes that let you create interactive menus in the console
"""
from dataclasses import dataclass, field
from console.inputs import SelectionInput, SelectionInputOptions, InputResult


@dataclass
class MenuOptions(SelectionInputOptions):
    recurring: bool = True
    cancel_codes: tuple = field(default_factory=tuple)


class Menu(SelectionInput):

    options_class = MenuOptions
    options: MenuOptions = None

    def __call__(self, prompt, commands, context=None, *args, **kwargs) -> InputResult:
        return self._invoke(prompt, commands, context=context, *args, **kwargs)

    def _invoke(self, prompt, commands, context=None, *args, **kwargs) -> InputResult:
        if context is None:
            context = {}
        names = list(commands.keys())
        result, selected_command_index = super()._invoke(prompt, names, *args, **kwargs)
        if result == InputResult.SUCCESS:
            commands.get(names[selected_command_index])(context)
        return result



        


