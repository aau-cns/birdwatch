from Settings import Settings
import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Callable, Optional, Any
from .tooltip import ToolTip


class CTkSwitch(ctk.CTkSwitch):
    def __init__(
        self,
        master: Any,
        width: int = 100,
        height: int = 24,
        switch_width: int = 36,
        switch_height: int = 18,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        button_length: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Union[str, Tuple[str, str]] = "transparent",
        progress_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        text: str = "CTkSwitch",
        font: Optional[Union[tuple, CTkFont]] = None,
        textvariable: Union[tkinter.Variable, None] = None,
        onvalue: Union[int, str] = 1,
        offvalue: Union[int, str] = 0,
        variable: Union[tkinter.Variable, None] = None,
        hover: bool = True,
        command: Union[Callable, Any] = None,
        state: str = tkinter.NORMAL,
        tooltip_text: Optional[Union[str, Tuple[str, str]]] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            switch_width=switch_width,
            switch_height=switch_height,
            corner_radius=corner_radius,
            border_width=border_width,
            button_length=button_length,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            progress_color=progress_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            text=text,
            font=font,
            textvariable=textvariable,
            onvalue=onvalue,
            offvalue=offvalue,
            variable=variable,
            state=state,
            hover=hover,
            command=command,
            **kwargs,
        )

        self._progress_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if progress_color is None and Settings.current_device is not None
            else self._check_color_type(progress_color, transparency=True)
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()

        self.configure(progress_color=Settings.current_device.color_theme.primary)
