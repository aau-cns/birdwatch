import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
from typing import Union, Tuple, Callable, List, Optional, Any
from .widget_tools import get_total_height

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class CTkScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master: Any,
        width: int = 200,
        height: int = 200,
        corner_radius: Optional[Union[int, str]] = None,
        border_width: Optional[Union[int, str]] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        scrollbar_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        scrollbar_button_color: Optional[Union[str, Tuple[str, str]]] = None,
        scrollbar_button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        label_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        label_text_color: Optional[Union[str, Tuple[str, str]]] = None,
        label_text: str = "",
        label_font: Optional[Union[tuple, CTkFont]] = None,
        label_anchor: str = "center",
        orientation: Literal["vertical", "horizontal"] = "vertical",
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            scrollbar_fg_color=scrollbar_fg_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
            label_fg_color=label_fg_color,
            label_text_color=label_text_color,
            label_text=label_text,
            label_font=label_font,
            label_anchor=label_anchor,
            orientation=orientation,
            **kwargs,
        )
        self.initial_kwargs = kwargs

        # Corrects for a bug in CustomTkinter that by default sets the height of the scrollbar to 200
        self._scrollbar.configure(height=0)

        self.bind_scroll_event()

    def refresh(self):
        master = self.master
        grid_info = self.grid_info()
        self.destroy()
        self.__init__(master, **self.initial_kwargs)
        if grid_info:
            self.grid(**grid_info)

    def refresh_root(self):
        level = self.get_root()
        level.refresh()
        level.set_tab()

    def get_root(self):
        level = self.master

        # Loop until reaching the Root Frame
        while not isinstance(level.master, ctk.CTk):
            level = level.master

        return level

    def bind_scroll_event(self):
        self.bind("<Enter>", self._bound_to_mousewheel)
        self.bind("<Leave>", self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.bind_all("<Button-4>", self._on_mousewheel)
        self.bind_all("<Button-5>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._parent_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._parent_canvas.yview_scroll(1, "units")

    def get_slaves_total_height(self) -> int:
        """
        Get the total height of all the widgets in the grid.

        Returns:
            int: The total height of all the widgets in the grid.
        """
        total_slaves_height = 0

        # Get number of rows
        rows = self.grid_size()[1]

        # For each row, get the heigh of the highest widget
        for row in range(rows):
            max_height = 0
            for widget in self.grid_slaves(row=row):
                height = get_total_height(widget)
                if height > max_height:
                    max_height = height

            total_slaves_height += max_height

        return total_slaves_height
