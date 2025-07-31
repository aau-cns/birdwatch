import customtkinter as ctk
from typing import Union, Tuple, Callable, Optional, Any
from .tooltip import ToolTip


class CTkScrollbar(ctk.CTkScrollbar):
    def __init__(
        self,
        master: Any,
        width: Optional[Union[int, str]] = None,
        height: Optional[Union[int, str]] = None,
        corner_radius: Optional[int] = None,
        border_spacing: Optional[int] = None,
        minimum_pixel_length: int = 20,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_color: Optional[Union[str, Tuple[str, str]]] = None,
        button_hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        hover: bool = True,
        command: Union[Callable, Any] = None,
        orientation: str = "vertical",
        tooltip_text: Optional[str] = None,
        tooltip_waittime: int = 500,
        **kwargs
    ):
        super().__init__(
            master,
            width=width,
            height=height,
            corner_radius=corner_radius,
            border_spacing=border_spacing,
            minimum_pixel_length=minimum_pixel_length,
            bg_color=bg_color,
            fg_color=fg_color,
            button_color=button_color,
            button_hover_color=button_hover_color,
            hover=hover,
            command=command,
            orientation=orientation,
            **kwargs,
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)
