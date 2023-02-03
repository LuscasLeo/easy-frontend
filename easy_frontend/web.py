import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Generic, List, Sequence, TypeVar, Union

from flask import Flask, make_response, request

from easy_frontend.actions import ActionsManager
from easy_frontend.renderer import CE, Button, Element, Script, Span, Text, View


class AdoptableStatus(Enum):
    AVAILABLE = "AVAILABLE"
    ADOPTED = "ADOPTED"
    PENDING = "PENDING"


@dataclass
class Adoptable:
    id: int
    name: str
    age: int
    breed: str
    description: str
    adoption_status: AdoptableStatus


adoptables = {
    1: Adoptable(1, "Fido", 3, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
    2: Adoptable(2, "Spot", 5, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
    3: Adoptable(3, "Rover", 1, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
}


def render_adoptables_table() -> View:
    return View(
        children=[
            CE(
                "table",
                [
                    CE(
                        "tr",
                        [
                            CE("th", [Text("ID")]),
                            CE("th", [Text("Name")]),
                            CE("th", [Text("Age")]),
                            CE("th", [Text("Breed")]),
                            CE("th", [Text("Description")]),
                            CE("th", [Text("Adoption Status")]),
                            CE("th", [Text("Adopt")]),
                        ],
                    ),
                    *[
                        CE(
                            "tr",
                            [
                                CE("td", [Text(str(adoptable.id))]),
                                CE("td", [Text(adoptable.name)]),
                                CE("td", [Text(str(adoptable.age))]),
                                CE("td", [Text(adoptable.breed)]),
                                CE("td", [Text(adoptable.description)]),
                                CE("td", [Text(adoptable.adoption_status.value)]),
                                CE(
                                    "td",
                                    [
                                        Button(
                                            [Text("Adopt")],
                                            attributes={
                                                "onclick": "execute_function('adopt', {id: __id})".replace(
                                                    "__id", str(adoptable.id)
                                                ),
                                                "class": "btn btn-success",
                                            },
                                            disabled=adoptable.adoption_status
                                            != AdoptableStatus.AVAILABLE,
                                        ),
                                        Button(
                                            [Text("Cancel Adoption")],
                                            attributes={
                                                "onclick": "execute_function('cancel_adoption', {id: __id})".replace(
                                                    "__id", str(adoptable.id)
                                                ),
                                                "class": "btn btn-danger",
                                            },
                                            disabled=adoptable.adoption_status
                                            != AdoptableStatus.PENDING,
                                        ),
                                    ],
                                ),
                            ],
                        )
                        for adoptable in adoptables.values()
                    ],
                ],
            ),
        ]
    )


def adopt(id: int) -> Any:
    if id not in adoptables:
        raise ValueError(f"Adoptable with id {id} does not exist")
    adoptable = adoptables[id]
    if adoptable.adoption_status != AdoptableStatus.AVAILABLE:
        raise ValueError(f"Adoptable with id {id} is not available")
    adoptable.adoption_status = AdoptableStatus.PENDING


def cancel_adoption(id: int) -> Any:
    if id not in adoptables:
        raise ValueError(f"Adoptable with id {id} does not exist")
    adoptable = adoptables[id]
    if adoptable.adoption_status != AdoptableStatus.PENDING:
        raise ValueError(f"Adoptable with id {id} is not pending")
    adoptable.adoption_status = AdoptableStatus.AVAILABLE


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
    callback: Callable[[IDENTITIFIER], Any] = field(
        default_factory=lambda: lambda id: None
    )


@dataclass
class TableView(Generic[T, IDENTITIFIER]):

    columns: List[Column]
    actions: Dict[str, Action[T, IDENTITIFIER]]

    id_getter: Callable[[T], IDENTITIFIER]

    id_to_str: Callable[[IDENTITIFIER], str]
    str_to_id: Callable[[str], IDENTITIFIER]

    column_getter: Callable[[T, str], str]

    def render(self, items: Sequence[T]) -> View:
        return View(
            children=[
                CE(
                    "table",
                    [
                        CE(
                            "tr",
                            [CE("th", [Text(column.label)]) for column in self.columns]
                            + [
                                CE("th", [Text(action.label)])
                                for action in self.actions.values()
                            ],
                        ),
                        *[
                            CE(
                                "tr",
                                [
                                    CE(
                                        "td",
                                        [Text(self.column_getter(item, column.name))],
                                    )
                                    for column in self.columns
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
                                                        self.id_to_str(
                                                            self.id_getter(item)
                                                        ),
                                                    ),
                                                    **action.attributes,
                                                },
                                                disabled=action.disabled(item),
                                            )
                                        ],
                                    )
                                    for action in self.actions.values()
                                ],
                            )
                            for item in items
                        ],
                    ],
                )
            ]
        )


AdoptableTable = TableView[Adoptable, int](
    column_getter=lambda adoptable, column_name: str(getattr(adoptable, column_name)),
    id_getter=lambda adoptable: adoptable.id,
    id_to_str=str,
    str_to_id=int,
    columns=[
        Column("id", "ID"),
        Column("name", "Name"),
        Column("age", "Age"),
        Column("breed", "Breed"),
        Column("description", "Description"),
        Column("adoption_status", "Adoption Status"),
    ],
    actions={
        "adopt": Action(
            "adopt",
            "Adopt",
            attributes={"class": "btn btn-success"},
            disabled=lambda adoptable: adoptable.adoption_status
            != AdoptableStatus.AVAILABLE,
            callback=adopt,
        ),
        "cancel_adoption": Action(
            "cancel_adoption",
            "Cancel Adoption",
            attributes={"class": "btn btn-danger"},
            disabled=lambda adoptable: adoptable.adoption_status
            != AdoptableStatus.PENDING,
            callback=cancel_adoption,
        ),
    },
)

app = Flask(__name__)


@app.route("/")
def list() -> Any:
    try:
        response = make_response(
            CE(
                "html",
                [
                    CE(
                        "head",
                        [
                            CE(
                                "link",
                                # Bootstrap
                                attributes={
                                    "rel": "stylesheet",
                                    "href": "https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css",
                                },
                            ),
                        ],
                    ),
                    CE(
                        "body",
                        [
                            Script(
                                """
function execute_function(action_name, item_id) {
    fetch("/", {
        method: "POST",
        body: JSON.stringify({action_name, item_id}),
        headers: {
            "Content-Type": "application/json"
        }
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        console.log(data);
        window.location.reload();
    });
}
            """
                            ),
                            CE(
                                "div",
                                [Text("Adoptables")],
                                attributes={"class": "container"},
                            ),
                            CE(
                                "div",
                                [AdoptableTable.render([*adoptables.values()])],
                                attributes={"class": "container"},
                            ),
                        ],
                    ),
                ],
            ).render()
        )
        response.headers["Refresh"] = "100"
        return response
    except Exception as e:
        response = make_response(
            View(
                children=[
                    Span(
                        [Text(e.__class__.__name__), Text(": "), Text(str(e))],
                        attributes={"style": "color: red"},
                    ),
                    View([CE("pre", [Text(traceback.format_exc())])]),
                ]
            ).render()
        )
        response.headers["Refresh"] = "100"
        return response


@app.route("/", methods=["POST"])
def action() -> Any:
    payload = request.json

    if payload is None:
        return {"success": False, "error": "No payload provided"}

    action_name = payload.get("action_name")
    if action_name is None:
        return {"success": False, "error": "No action_name provided"}

    item_id = payload.get("item_id")
    if item_id is None:
        return {"success": False, "error": "No item_id provided"}

    action = AdoptableTable.actions.get(action_name)
    if action is None:
        return {"success": False, "error": "Invalid action_name provided"}

    try:
        result = action.callback(item_id)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
