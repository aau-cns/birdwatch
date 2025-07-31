from Settings import Settings
import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Callable, List, Optional, Any
from .tooltip import ToolTip


class CTkRadioButton(ctk.CTkRadioButton):
    def __init__(
        self,
        master: Any,
        width: int = 100,
        height: int = 22,
        radiobutton_width: int = 22,
        radiobutton_height: int = 22,
        corner_radius: Optional[int] = None,
        border_width_unchecked: Optional[int] = None,
        border_width_checked: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        text: str = "CTkRadioButton",
        font: Optional[Union[tuple, CTkFont]] = None,
        textvariable: Union[tkinter.Variable, None] = None,
        variable: Union[tkinter.Variable, None] = None,
        value: Union[int, str] = 0,
        state: str = tkinter.NORMAL,
        hover: bool = True,
        command: Union[Callable, Any] = None,
        tooltip_text: Optional[Union[str, Tuple[str, str]]] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            radiobutton_width=radiobutton_width,
            radiobutton_height=radiobutton_height,
            corner_radius=corner_radius,
            border_width_unchecked=border_width_unchecked,
            border_width_checked=border_width_checked,
            bg_color=bg_color,
            fg_color=fg_color,
            hover_color=hover_color,
            border_color=border_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            text=text,
            font=font,
            textvariable=textvariable,
            variable=variable,
            value=value,
            state=state,
            hover=hover,
            command=command,
            **kwargs,
        )

        self._fg_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if fg_color is None and Settings.current_device is not None
            else self._check_color_type(fg_color)
        )
        self._hover_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.dark_primary
            if hover_color is None and Settings.current_device is not None
            else self._check_color_type(hover_color)
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()
