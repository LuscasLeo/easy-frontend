from inspect import signature
from typing import Any, Callable, Union

from easy_frontend.renderer.basic_renderer import CE, Element, Text, View


def describe_type(t: Any) -> str:
    if isinstance(t, type):
        return t.__name__
    ## if is a typing generic type
    if hasattr(t, "__origin__"):
        if t.__origin__ is list:
            return "List[{}]".format(describe_type(t.__args__[0]))
        if t.__origin__ is dict:
            return "Dict[{}, {}]".format(
                describe_type(t.__args__[0]), describe_type(t.__args__[1])
            )
        if t.__origin__ == Union:
            if t.__args__[1] == type(None):
                return "Optional[{}]".format(describe_type(t.__args__[0]))
            return "Union[{}]".format(
                ", ".join(describe_type(arg) for arg in t.__args__)
            )

    return "UnknownType"


def map_function(func: Callable) -> Element:

    sig = signature(func)

    return CE(
        "PRE",
        [
            Text(
                """
{func_name}({func_args})
""".format(
                    func_name=func.__name__,
                    func_args=", ".join(
                        [
                            "{}: {}.{}".format(
                                param.name,
                                param.annotation.__module__,
                                describe_type(param.annotation)
                                if param.annotation != param.empty
                                else "Any",
                            )
                            for param in sig.parameters.values()
                        ]
                    ),
                )
            )
        ],
    )
