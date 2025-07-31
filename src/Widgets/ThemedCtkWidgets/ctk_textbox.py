import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from typing import Union, Tuple, Optional
from .tooltip import ToolTip


class CTkTextbox(ctk.CTkTextbox):
    def __init__(
        self,
        master: any,
        width: int = 200,
        height: int = 200,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        border_spacing: int = 3,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, str]] = None,
        scrollbar_button_color: Optional[Union[str, Tuple[str, str]]] = None,
        scrollbar_button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        font: Optional[Union[tuple, CTkFont]] = None,
        activate_scrollbars: bool = True,
        tooltip_text: Optional[str] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_width=border_width,
            border_spacing=border_spacing,
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            text_color=text_color,
            scrollbar_button_color=scrollbar_button_color,
            scrollbar_button_hover_color=scrollbar_button_hover_color,
            font=font,
            activate_scrollbars=activate_scrollbars,
            **kwargs,
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)
