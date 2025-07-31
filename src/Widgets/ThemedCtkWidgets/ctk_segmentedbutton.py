from Settings import Settings
import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Callable, Optional, Any


class CTkSegmentedButton(ctk.CTkSegmentedButton):
    def __init__(
        self,
        master: Any,
        width: int = 140,
        height: int = 28,
        corner_radius: Optional[int] = None,
        border_width: int = 3,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        selected_color: Optional[Union[str, Tuple[str, str]]] = None,
        selected_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        unselected_color: Optional[Union[str, Tuple[str, str]]] = None,
        unselected_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        background_corner_colors: Union[
            Tuple[Union[str, Tuple[str, str]]], None
        ] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        values: Optional[list] = None,
        variable: Union[tkinter.Variable, None] = None,
        dynamic_resizing: bool = True,
        command: Union[Callable[[str], Any], None] = None,
        state: str = "normal",
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            bg_color=bg_color,
            fg_color=fg_color,
            selected_color=selected_color,
            selected_hover_color=selected_hover_color,
            unselected_color=unselected_color,
            unselected_hover_color=unselected_hover_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            background_corner_colors=background_corner_colors,
            font=font,
            values=values,
            variable=variable,
            dynamic_resizing=dynamic_resizing,
            command=command,
            state=state,
        )

        self._selected_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if selected_color is None and Settings.current_device is not None
            else self._check_color_type(selected_color)
        )
        self._selected_hover_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.dark_primary
            if selected_hover_color is None and Settings.current_device is not None
            else self._check_color_type(selected_hover_color)
        )

        self._draw()
