import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Callable, List, Optional, Any
from .tooltip import ToolTip


class CTkComboBox(ctk.CTkComboBox):
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
        button_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        dropdown_text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        dropdown_font: Optional[Union[tuple, CTkFont]] = None,
        values: Optional[List[str]] = None,
        state: str = tkinter.NORMAL,
        hover: bool = True,
        variable: Union[tkinter.Variable, None] = None,
        command: Union[Callable[[str], Any], None] = None,
        justify: str = "left",
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
            button_color=button_color,
            button_hover_color=button_hover_color,
            dropdown_fg_color=dropdown_fg_color,
            dropdown_hover_color=dropdown_hover_color,
            dropdown_text_color=dropdown_text_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            font=font,
            dropdown_font=dropdown_font,
            values=values,
            state=state,
            hover=hover,
            variable=variable,
            command=command,
            justify=justify,
            **kwargs,
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)
