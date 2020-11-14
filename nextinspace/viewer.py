"""Viewer for terminal output"""

from colorama import deinit, init

from nextinspace import space


def display_list(items_list, verbosity):
    if len(items_list) == 0:
        return

    show_top()

    # For compatibility with Windows terminals
    init()
    items_list[0].display(verbosity)
    for item in items_list[1:]:
        show_divider()
        item.display(verbosity)
    deinit()

    show_bottom()


def show_top():
    print("┌" + "─" * space.MAX_LINE_LENGTH + "┐")


def show_divider():
    print("├" + "─" * space.MAX_LINE_LENGTH + "┤")


def show_bottom():
    print("└" + "─" * space.MAX_LINE_LENGTH + "┘")
