import customtkinter as ctk
from typing import Union, Tuple, Optional
import Widgets.ThemedCtkWidgets as tcw
from Settings import Settings


class CollapsibleFrame(tcw.CTkFrame):
    def __init__(
        self,
        master,
        title,
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
    ):
        """
        Initialize a collapsible frame with a title.

        Parameters:
            master: The parent widget.
            title (str): The title of the collapsible frame.
            fg_color (optional): The foreground color of the frame.
            border_color (optional): The color of the border of the frame.

        Description:
            This class creates a frame that can be collapsed or expanded.
            It includes a header with a title and an expand/collapse button.

        Example:
            collapsable_frame = CollapsableFrame.CollapsableFrame(
                some_frame,
                "Example title"
            )

            collapsable_frame.set_subwidget(
                customtkinter.CTkLabel(collapsable_frame, text="subwidget"),
                expand=True
            )

            collapsable_frame.grid(row=3, column=0)
        """
        super().__init__(master, fg_color=fg_color, border_color=border_color)

        if border_color is not None:
            self.configure(border_width=2)

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)

        # Define frame for the title and collapse/expand button
        self.header_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.header_frame.columnconfigure(0, weight=1)
        self.header_frame.grid(row=0, column=0, sticky="new")

        # Add title
        self.title = tcw.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(weight="bold"),
            fg_color=Settings.current_device.color_theme.primary,
            corner_radius=6,
        )
        self.title.grid(row=0, column=0, sticky="new")

        # Add collapse/expand button
        self.expand_button = tcw.CTkButton(
            self.header_frame,
            text="  ▴  ",
            command=self.toggle_expand,
            width=0,
        )
        self.expand_button.grid(row=0, column=1, padx=(5, 0), sticky="new")

        self.expand = ctk.BooleanVar(value=True)

        # Add default subwidget
        self.subwidget: ctk.CTkBaseClass = None

    def toggle_expand(self):
        """
        Toggle between expanding and collapsing the frame.

        Description:
            This method toggles the state of the collapsible frame.
            It expands or collapses the frame based on its current state.
        """
        if self.expand.get():
            self.expand.set(False)
            self.subwidget.grid_forget()
            self.expand_button.configure(text="  ▾  ")
        else:
            self.expand.set(True)
            self.subwidget.grid(
                row=1,
                padx=self.cget("border_width") + 1,
                pady=(5, self.cget("border_width") + 1),
                column=0,
                sticky="nesw",
            )
            self.expand_button.configure(text="  ▴  ")

    def set_subwidget(self, subwidget: ctk.CTkBaseClass, expand=False):
        """
        Set the subwidget within the collapsible frame.

        Parameters:
            subwidget (ctk.CTkBaseClass): The subwidget to be placed within the frame.
            expand (bool): Whether to expand the frame initially. Default = False

        Description:
            This method sets a subwidget within the collapsible frame.
            It also specifies whether the frame should be expanded initially.
        """
        self.subwidget = subwidget
        self.subwidget.grid(
            row=1,
            padx=self.cget("border_width") + 1,
            pady=(5, self.cget("border_width") + 1),
            column=0,
            sticky="nesw",
        )
        if not expand:
            self.toggle_expand()
