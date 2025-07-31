from Settings import Settings
import tkinter
import customtkinter as ctk
from typing import Union, Tuple, Callable, Optional, Any
from .tooltip import ToolTip


class CTkSlider(ctk.CTkSlider):
    def __init__(
        self,
        master: Any,
        width: Optional[int] = None,
        height: Optional[int] = None,
        corner_radius: Optional[int] = None,
        button_corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        button_length: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Union[str, Tuple[str, str]] = "transparent",
        progress_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        from_: int = 0,
        to: int = 1,
        state: str = "normal",
        number_of_steps: Union[int, None] = None,
        hover: bool = True,
        command: Union[Callable[[float], Any], None] = None,
        variable: Union[tkinter.Variable, None] = None,
        orientation: str = "horizontal",
        tooltip_text: Optional[Union[str, Tuple[str, str]]] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            button_corner_radius=button_corner_radius,
            border_width=border_width,
            button_length=button_length,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            progress_color=progress_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            from_=from_,
            to=to,
            state=state,
            number_of_steps=number_of_steps,
            hover=hover,
            command=command,
            variable=variable,
            orientation=orientation,
            **kwargs,
        )

        self._button_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if button_color is None and Settings.current_device is not None
            else self._check_color_type(button_color)
        )
        self._button_hover_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.dark_primary
            if button_hover_color is None and Settings.current_device is not None
            else self._check_color_type(button_hover_color)
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()
