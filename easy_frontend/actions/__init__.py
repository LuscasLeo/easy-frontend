from typing import Any, Callable, Dict


class ActionsManager:

    def __init__(self, actions: Dict[str, Callable]) -> None:
        self.actions = actions

    def execute(self, action_name: str, args: Dict[str, Any]) -> Any:
        return self.actions[action_name](**args)
        