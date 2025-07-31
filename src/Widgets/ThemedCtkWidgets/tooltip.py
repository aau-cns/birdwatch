import customtkinter as ctk
from typing import Union, Tuple, List


class ToolTip:

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        text: Union[str, Tuple[str, str]],
        waittime: int = 2000,
    ):
        """
        Creates a tooltip for a master widget. The tooltip is shown when the
        mouse hovers over the master widget.

        Parameters:
            master: the parent widget
            text (string or tuple): the text to show in the tooltip. If a tuple
                                    is given, the first element is the text to show
                                    when the master widget is enabled and the second
                                    element is the text to show when the master widget
                                    is disabled. If the text is a tuple and either of
                                    the elements is an empty string, the tooltip will
                                    not be shown for that state.
            waittime (optional, int): time in milliseconds to wait before showing the
                                    tooltip. Default: 500
        """
        self.master = master
        self.text = text
        self.waittime = waittime
        self.tooltip = None
        self.id = None

        self.master.bind("<Enter>", self.on_enter)
        self.master.bind("<Leave>", self.on_leave)

    def on_enter(self, event):
        self.schedule()

    def on_leave(self, event):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.master.after(self.waittime, self.showtip)

        # Add the tooltip to the active tooltips list
        ToolTipManager.add_tooltip(self)

    def unschedule(self):
        if self.id is not None:
            self.master.after_cancel(self.id)
            self.id = None

        # Remove the tooltip from the active tooltips list
        ToolTipManager.remove_tooltip(self)

    def showtip(self):

        # Decide which text to show based on the state of the master widget
        text = None
        if isinstance(self.text, str):
            if self.text != "":
                text = self.text
            else:
                return
        elif isinstance(self.text, tuple):
            try:
                state = self.master.cget("state")
            except:
                return

            if state == "normal":
                if self.text[0] != "":
                    text = self.text[0]
                else:
                    return
            else:
                if self.text[1] != "":
                    text = self.text[1]
                else:
                    return
        else:
            return

        # Create the tooltip
        self.tooltip = ctk.CTkToplevel(self.master)

        # Position the tooltip below the master widget
        self.tooltip.wm_geometry(
            "+{x}+{y}".format(
                x=self.master.winfo_rootx() + 25,
                y=self.master.winfo_rooty() + 2 + self.master.winfo_height(),
            )
        )

        self.tooltip.configure(fg_color="gray60")

        # Remove the window decorations (only the label will be shown)
        self.tooltip.wm_overrideredirect(True)

        # Add the text to the tooltip
        self.label = ctk.CTkLabel(self.tooltip, text=text, text_color="black")
        self.label.grid(row=0, column=0, padx=5)

    def hidetip(self):
        # Remove the tooltip from the active tooltips list
        ToolTipManager.remove_tooltip(self)

        # Destroy the tooltip
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


class ToolTipManager:
    """
    Manages the active tooltips.
    """

    __active_tooltips: List[ToolTip] = []

    @classmethod
    def add_tooltip(cls, tooltip: ToolTip):
        """
        Add a tooltip to the active tooltips list.

        Parameters:
            tooltip (ToolTip): The tooltip to add to the active tooltips list.
        """
        cls.__active_tooltips.append(tooltip)

    @classmethod
    def remove_tooltip(cls, tooltip: ToolTip):
        """
        Remove a tooltip from the active tooltips list.

        Parameters:
            tooltip (ToolTip): The tooltip to remove from the active tooltips list.
        """
        if tooltip in cls.__active_tooltips:
            cls.__active_tooltips.remove(tooltip)

    @classmethod
    def hide_all(cls):
        """
        Hide all active tooltips.
        """
        for tooltip in cls.__active_tooltips:
            tooltip.unschedule()
            tooltip.hidetip()
        cls.__active_tooltips.clear()
