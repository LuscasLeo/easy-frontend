from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class Element(ABC):
    def __init__(
        self,
        children: List["Element"] = [],
        attributes: Dict[str, str] = {},
    ) -> None:
        self.children = children
        self.attributes = attributes

    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError

    def render_recursive(self) -> str:
        return "".join(child.render() for child in self.children)

    def render_open_element(self, tag_name: str) -> str:
        return "<{tag_name}{attributes}>".format(
            tag_name=tag_name,
            attributes=self.render_attributes(),
        )

    def render_attributes(self) -> str:
        return "".join(
            ' {}="{}"'.format(key, self.escape_attribute_value(value))
            for key, value in self.attributes.items()
        )

    def escape_attribute_value(self, value: str) -> str:
        return value.replace('"', '\\"')

    def render_close_element(self, tag_name: str) -> str:
        return "</{tag_name}>".format(tag_name=tag_name)

    def render_element(self, element_name: str) -> str:
        return "{open_element}{children}{close_element}".format(
            open_element=self.render_open_element(element_name),
            children="".join(child.render() for child in self.children),
            close_element=self.render_close_element(element_name),
        )


class Renderable(Element, ABC):
    @abstractmethod
    def render(self) -> str:
        raise NotImplementedError


class Button(Element):
    def __init__(
        self,
        children: List["Element"] = [],
        attributes: Dict[str, str] = {},
        disabled: bool = False,
    ) -> None:
        super().__init__(
            children, {**attributes, **({"disabled": "disabled"} if disabled else {})}
        )

    def render(self) -> str:
        return self.render_element("button")


class View(Element):
    def render(self) -> str:
        return self.render_element("div")


class Text(Renderable):
    def __init__(self, text: str):
        self.text = text

    def render(self) -> str:
        return self.text.replace("<", "&lt;").replace(">", "&gt;")


class Script(Element):
    def __init__(
        self,
        script: Optional[str] = None,
        src: Optional[str] = None,
        attributes: Dict[str, str] = {},
    ) -> None:
        super().__init__(
            [Text(script)] if script else [],
            {**attributes, **({"src": src} if src else {})},
        )

    def render(self) -> str:
        return self.render_element("script")


class CustomElement(Element):
    def __init__(
        self,
        tag_name: str,
        children: List[Element] = [],
        attributes: Dict[str, str] = {},
    ) -> None:
        super().__init__(children, attributes)
        self.tag_name = tag_name

    def render(self) -> str:
        return self.render_element(self.tag_name)


CE = CustomElement


class Span(Element):
    def render(self) -> str:
        return self.render_element("span")
