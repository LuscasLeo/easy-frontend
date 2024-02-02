from typing import Any, Callable, Sequence, TypeVar

from easy_frontend.objects import TableView
from easy_frontend.renderer.basic_renderer import CE, Button, Text, View

T = TypeVar("T")
ID = TypeVar("ID")


def render_table_view(table_view: TableView[T, ID], items: Sequence[T]) -> View:
    return View(
        children=[
            CE(
                "table",
                [
                    CE(
                        "tr",
                        [
                            CE("th", [Text(column.label)])
                            for column in table_view.columns
                        ]
                        + [
                            CE("th", [Text(action.label)])
                            for action in table_view.actions.values()
                        ],
                    ),
                    *[
                        CE(
                            "tr",
                            [
                                CE(
                                    "td",
                                    [Text(table_view.column_getter(item, column.name))],
                                )
                                for column in table_view.columns
                            ]
                            + [
                                CE(
                                    "td",
                                    [
                                        Button(
                                            [Text(action.label)],
                                            attributes={
                                                "onclick": "execute_function('__action_name', __id)".replace(
                                                    "__action_name", action.name
                                                ).replace(
                                                    "__id",
                                                    table_view.id_to_str(
                                                        table_view.id_getter(item)
                                                    ),
                                                ),
                                                **action.attributes,
                                            },
                                            disabled=action.disabled(item),
                                        )
                                    ],
                                )
                                for action in table_view.actions.values()
                            ],
                        )
                        for item in items
                    ],
                ],
            )
        ]
    )


ActionToJS = Callable[[Callable[..., None]], str]
