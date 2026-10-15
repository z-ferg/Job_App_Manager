"""Start the Textual TUI frontend application."""
from textual.app import App


class JamTUI(App):
    ...

def main(argc: int, argv: list[str]) -> None:
    app = JamTUI()
    app.run()