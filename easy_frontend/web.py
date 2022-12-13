from dataclasses import dataclass
import traceback
from typing import Any

from flask import Flask, make_response, request

from easy_frontend.mapper import map_function
from easy_frontend.renderer import CE, Script, Span, Text, View

from enum import Enum


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


adoptables = [
    Adoptable(1, "Fido", 3, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
    Adoptable(2, "Spot", 5, "Pitbull", "A good dog", AdoptableStatus.ADOPTED),
    Adoptable(3, "Rover", 1, "Pitbull", "A good dog", AdoptableStatus.PENDING),
]

def render_adoptables_table() -> View:
    return View(
        children=[
            Script("""
                function execute_function(name, args) {
                    fetch("/", {
                        method: "POST",
                        body: JSON.stringify(args),
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
            """),
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
                            CE("th", [Text("Adopt")])
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
                                CE("td", [CE("button", [Text("Adopt")], attributes={"onclick": "execute_function('adopt', {id: __id})".replace("__id", str(adoptable.id))})]),
                            ],
                        )
                        for adoptable in adoptables
                    ],
                ],
            )
        ]
    )



app = Flask(__name__)


@app.route("/")
def list() -> Any:
    try:
        response = make_response(render_adoptables_table().render())
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

    id = payload["id"]
    try:
        adoptable = next(adoptable for adoptable in adoptables if adoptable.id == id)
        adoptable.adoption_status = AdoptableStatus.ADOPTED
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
