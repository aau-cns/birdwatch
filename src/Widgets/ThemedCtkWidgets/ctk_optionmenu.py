from Settings import Settings
import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Callable, Optional, Any
from .tooltip import ToolTip


class CTkOptionMenu(ctk.CTkOptionMenu):
    def __init__(
        self,
        master: Any,
        width: int = 140,
        height: int = 28,
        corner_radius: Optional[Union[int]] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_text_color: Optional[Union[str, Tuple[str, str]]] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        dropdown_font: Optional[Union[tuple, CTkFont]] = None,
        values: Optional[list] = None,
        variable: Union[tkinter.Variable, None] = None,
        state: str = tkinter.NORMAL,
        hover: bool = True,
        command: Union[Callable[[str], Any], None] = None,
        dynamic_resizing: bool = True,
        anchor: str = "w",
        tooltip_text: Optional[Union[str, Tuple[str, str]]] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            bg_color=bg_color,
            fg_color=fg_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            dropdown_fg_color=dropdown_fg_color,
            dropdown_hover_color=dropdown_hover_color,
            dropdown_text_color=dropdown_text_color,
            font=font,
            dropdown_font=dropdown_font,
            values=values,
            variable=variable,
            state=state,
            hover=hover,
            command=command,
            dynamic_resizing=dynamic_resizing,
            anchor=anchor,
            **kwargs,
        )

        self._fg_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if fg_color is None and Settings.current_device is not None
            else self._check_color_type(fg_color)
        )
        self._button_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.dark_primary
            if button_color is None and Settings.current_device is not None
            else self._check_color_type(button_color)
        )
        self._button_hover_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.darker_primary
            if button_hover_color is None and Settings.current_device is not None
            else self._check_color_type(button_hover_color)
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()
