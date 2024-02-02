import traceback
from dataclasses import dataclass
from enum import Enum
from typing import Any

from flask import Flask, make_response, request

from easy_frontend.objects import Action, Column, TableView
from easy_frontend.renderer.basic_renderer import CE, Span, Text, View

## Domain Model
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


## Domain Data
adoptables = {
    1: Adoptable(1, "Fido", 3, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
    2: Adoptable(2, "Spot", 5, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
    3: Adoptable(3, "Rover", 1, "Pitbull", "A good dog", AdoptableStatus.AVAILABLE),
}

## Domain Logic
def adopt(id: int) -> Any:
    if id not in adoptables:
        raise ValueError(f"Adoptable with id {id} does not exist")
    adoptable = adoptables[id]
    if adoptable.adoption_status != AdoptableStatus.AVAILABLE:
        raise ValueError(f"Adoptable with id {id} is not available")
    adoptable.adoption_status = AdoptableStatus.PENDING

## Domain Logic
def cancel_adoption(id: int) -> Any:
    if id not in adoptables:
        raise ValueError(f"Adoptable with id {id} does not exist")
    adoptable = adoptables[id]
    if adoptable.adoption_status != AdoptableStatus.PENDING:
        raise ValueError(f"Adoptable with id {id} is not pending")
    adoptable.adoption_status = AdoptableStatus.AVAILABLE


## Domain Presentation
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
        ),
        "cancel_adoption": Action(
            "cancel_adoption",
            "Cancel Adoption",
            attributes={"class": "btn btn-danger"},
            disabled=lambda adoptable: adoptable.adoption_status
            != AdoptableStatus.PENDING,
        ),
    },
)


@dataclass
class DOM:
    ...    

## Web Port (Flask)
app = Flask(__name__)


def list() -> Any:
    try:
        response = make_response()
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
