import customtkinter as ctk


def get_total_height(widget: ctk.CTkBaseClass):
    """
    Get the total height of a widget.

    Parameters:
        widget: The widget to get the height of.

    Returns:
        The total height of the widget.
    """
    widget.update()

    padding_y = widget.grid_info().get("pady", 0)
    if isinstance(padding_y, tuple):
        padding_y = sum(padding_y)
    else:
        padding_y *= 2

    return widget.winfo_reqheight() + padding_y
