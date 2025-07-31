import customtkinter as ctk
from typing import Union, Tuple, Optional, Any
from .widget_tools import get_total_height


class CTkFrame(ctk.CTkFrame):
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
        background_corner_colors: Union[
            Tuple[Union[str, Tuple[str, str]]], None
        ] = None,
        overwrite_preferred_drawing_method: Union[str, None] = None,
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
            background_corner_colors=background_corner_colors,
            overwrite_preferred_drawing_method=overwrite_preferred_drawing_method,
            **kwargs,
        )
        self.initial_kwargs = kwargs

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
