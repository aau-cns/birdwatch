import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Optional, Any
from .tooltip import ToolTip


class CTkEntry(ctk.CTkEntry):
    def __init__(
        self,
        master: Any,
        width: int = 140,
        height: int = 28,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        placeholder_text_color: Optional[Union[str, Tuple[str, str]]] = None,
        textvariable: Union[tkinter.Variable, None] = None,
        placeholder_text: Union[str, None] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        state: str = tkinter.NORMAL,
        tooltip_text: Optional[Union[str, Tuple[str, str]]] = None,
        tooltip_waittime: int = 500,
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
            text_color=text_color,
            placeholder_text_color=placeholder_text_color,
            textvariable=textvariable,
            placeholder_text=placeholder_text,
            font=font,
            state=state,
            **kwargs,
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)
