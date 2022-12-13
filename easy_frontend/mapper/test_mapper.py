class TestMapper:
    def render_simple_function(self) -> None:
        def simple_function() -> str:
            return "Hello world"

        assert simple_function() == "Hello world"
