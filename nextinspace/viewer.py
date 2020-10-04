"""Viewer for terminal output"""

from nextinspace import space


def display_list(items_list, verbosity):
    _show_top()
    items_list[0].display(verbosity)
    for s in items_list[1:]:
        _show_divider()
        s.display(verbosity)
    _show_bottom()


def _show_top():
    print("┌" + "─" * space.MAX_LINE_LENGTH + "┐")


def _show_divider():
    print("├" + "─" * space.MAX_LINE_LENGTH + "┤")


def _show_bottom():
    print("└" + "─" * space.MAX_LINE_LENGTH + "┘")
