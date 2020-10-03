"""The viewer for terminal output"""

from nextinspace import space


def display_list(space_list, verbosity):
    _show_top()
    space_list[0].display(verbosity)
    for s in space_list[1:]:
        _show_divider()
        s.display(verbosity)
    _show_bottom()


def _show_top():
    print("┌" + "─" * space.MAX_LINE_LENGTH + "┐")


def _show_divider():
    print("├" + "─" * space.MAX_LINE_LENGTH + "┤")


def _show_bottom():
    print("└" + "─" * space.MAX_LINE_LENGTH + "┘")
