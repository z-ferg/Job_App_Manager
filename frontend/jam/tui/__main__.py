"""Start the Textual TUI frontend application."""

from frontend.jam.tui.app import JamApp


def main() -> None:
    JamApp().run()
