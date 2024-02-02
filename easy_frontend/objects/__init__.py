from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, TypeVar


@dataclass
class Column:
    name: str
    label: str


T = TypeVar("T")
IDENTITIFIER = TypeVar("IDENTITIFIER")


@dataclass
class Action(Generic[T, IDENTITIFIER]):
    name: str
    label: str
    attributes: Dict[str, str] = field(default_factory=dict)
    disabled: Callable[[T], bool] = field(default_factory=lambda: lambda row: False)


@dataclass
class TableView(Generic[T, IDENTITIFIER]):

    columns: List[Column]
    actions: Dict[str, Action[T, IDENTITIFIER]]

    id_getter: Callable[[T], IDENTITIFIER]

    id_to_str: Callable[[IDENTITIFIER], str]
    str_to_id: Callable[[str], IDENTITIFIER]

    column_getter: Callable[[T, str], str]
