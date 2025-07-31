from Settings import Settings
import tkinter
import customtkinter as ctk
from customtkinter.windows.widgets.font import CTkFont
from customtkinter.windows.widgets.image import CTkImage
from typing import Union, Tuple, Callable, Optional, Any
from .tooltip import ToolTip


class CTkButton(ctk.CTkButton):
    def __init__(
        self,
        master: Any,
        width: int = 140,
        height: int = 28,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        border_spacing: int = 2,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        hover_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        background_corner_colors: Union[
            Tuple[Union[str, Tuple[str, str]]], None
        ] = None,
        round_width_to_even_numbers: bool = True,
        round_height_to_even_numbers: bool = True,
        text: str = "CTkButton",
        font: Optional[Union[tuple, CTkFont]] = None,
        textvariable: Union[tkinter.Variable, None] = None,
        image: Union[CTkImage, "ImageTk.PhotoImage", None] = None,
        state: str = "normal",
        hover: bool = True,
        command: Union[Callable[[], Any], None] = None,
        compound: str = "left",
        anchor: str = "center",
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
            border_spacing=border_spacing,
            bg_color=bg_color,
            fg_color=fg_color,
            hover_color=hover_color,
            border_color=border_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            background_corner_colors=background_corner_colors,
            round_width_to_even_numbers=round_width_to_even_numbers,
            round_height_to_even_numbers=round_height_to_even_numbers,
            text=text,
            font=font,
            textvariable=textvariable,
            image=image,
            state=state,
            hover=hover,
            command=command,
            compound=compound,
            anchor=anchor,
            **kwargs,
        )

        self._fg_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if fg_color is None and Settings.current_device is not None
            else fg_color
        )
        self._hover_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.dark_primary
            if hover_color is None and Settings.current_device is not None
            else hover_color
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()
