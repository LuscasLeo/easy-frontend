from dataclasses import dataclass

from easy_frontend.renderer.basic_renderer import (CE, Button, CustomElement,
                                                   Script, Span, Text, View)


class TestGenerateHtmlFromView:

    # def test_render_function(self):

    #     @dataclass
    #     class Pet:
    #         pet_id: int
    #         name: str
    #         age: int

    #     def adopt_pet(pet_id: int) -> Pet:
    #         return "Pet {} adopted".format(pet_id)

    #     view = View(
    #         children=[
    #             View(
    #                 children=[
    #                     Text("Pet name: "),
    #                     Text("{{ pet.name }}"),
    #                     Button("Adopt", "adopt_pet", pet_id="{{ pet.pet_id }}"),

    #                 ],
    #             )

    #         ]
    #     )

    def test_render_view(self) -> None:
        view = View()

        assert view.render() == "<div></div>"

    def test_render_view_with_text(self) -> None:
        view = View(children=[Text("Hello world")])

        assert view.render() == "<div>Hello world</div>"

    def test_render_view_with_unescaped_angle_brackets(self) -> None:
        view = View(children=[Text("Hello <world>")])

        assert view.render() == "<div>Hello &lt;world&gt;</div>"

    def test_render_view_with_escaped_angle_brackets(self) -> None:
        view = View(children=[Text("Hello &lt;world&gt;")])

        assert view.render() == "<div>Hello &lt;world&gt;</div>"

    def test_render_button(self) -> None:
        button = Button(children=[Text("Adopt")])

        assert button.render() == "<button>Adopt</button>"

    def test_render_view_with_button(self) -> None:
        view = View(children=[Button(children=[Text("Adopt")])])

        assert view.render() == "<div><button>Adopt</button></div>"

    def test_render_view_with_button_with_attribute(self) -> None:
        button = Button(children=[Text("Adopt")], attributes={"id": "adopt-button"})

        assert button.render() == '<button id="adopt-button">Adopt</button>'

    def test_render_view_with_button_with_multiple_attributes(self) -> None:
        button = Button(
            children=[Text("Adopt")],
            attributes={"id": "adopt-button", "class": "button"},
        )

        assert (
            button.render() == '<button id="adopt-button" class="button">Adopt</button>'
        )

    def test_escape_quote_in_attribute_value(self) -> None:
        button = Button(
            children=[Text("Adopt")],
            attributes={"id": "adopt-button", "class": 'button"'},
        )

        assert (
            button.render()
            == '<button id="adopt-button" class="button\\"">Adopt</button>'
        )

    def test_script_elememt(self) -> None:
        script = Script("alert('Hello world')")

        assert script.render() == "<script>alert('Hello world')</script>"
    
    def test_script_with_src(self) -> None:
        script = Script(src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js")

        assert script.render() == '<script src="https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js"></script>'

    def test_custom_element(self) -> None:

        custom_element = CustomElement("custom")

        assert custom_element.render() == "<custom></custom>"

        ce = CE("custom")

        assert ce.render() == "<custom></custom>"

    def test_span_element(self) -> None:

        span = Span()
        assert span.render() == "<span></span>"