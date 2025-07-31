import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
from typing import Union, Tuple, Optional, Any
from .tooltip import ToolTip


class CTkLabel(ctk.CTkLabel):
    def __init__(
        self,
        master: Any,
        width: int = 0,
        height: int = 28,
        corner_radius: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        text: str = "CTkLabel",
        font: Optional[Union[tuple, CTkFont]] = None,
        image: Union[CTkImage, None] = None,
        compound: str = "center",
        anchor: str = "center",  # label anchor: center, n, e, s, w
        wraplength: int = 0,
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
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            text=text,
            font=font,
            image=image,
            compound=compound,
            anchor=anchor,
            wraplength=wraplength,
            **kwargs,
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)
