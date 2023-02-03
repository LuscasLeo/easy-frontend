import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flask import Flask, make_response, request

from easy_frontend.actions import ActionsManager
from easy_frontend.renderer import CE, Button, Script, Span, Text, View


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
            Script(
                """
function execute_function(action_name, args) {
    fetch("/", {
        method: "POST",
        body: JSON.stringify({action_name, args}),
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


action_manager = ActionsManager(
    {
        "adopt": adopt,
        "cancel_adoption": cancel_adoption,
    }
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
                            CE(
                                "div",
                                [Text("Adoptables")],
                                attributes={"class": "container"},
                            ),
                            CE(
                                "div",
                                [render_adoptables_table()],
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

    args = payload.get("args")
    if args is None:
        return {"success": False, "error": "No args provided"}

    try:
        result = action_manager.execute(action_name, args)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
