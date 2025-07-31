from Settings import Settings
import tkinter
import customtkinter as ctk
from typing import Union, Tuple, Optional, Any
from .tooltip import ToolTip

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class CTkProgressBar(ctk.CTkProgressBar):
    def __init__(
        self,
        master: Any,
        width: Optional[int] = None,
        height: Optional[int] = None,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        progress_color: Optional[Union[str, Tuple[str, str]]] = None,
        variable: Union[tkinter.Variable, None] = None,
        orientation: str = "horizontal",
        mode: Literal["determinate", "indeterminate"] = "determinate",
        determinate_speed: float = 1,
        indeterminate_speed: float = 1,
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
            bg_color=bg_color,
            fg_color=fg_color,
            border_color=border_color,
            progress_color=progress_color,
            variable=variable,
            orientation=orientation,
            mode=mode,
            determinate_speed=determinate_speed,
            indeterminate_speed=indeterminate_speed,
            **kwargs,
        )

        self._progress_color: Union[str, Tuple[str, str]] = (
            Settings.current_device.color_theme.primary
            if progress_color is None and Settings.current_device is not None
            else self._check_color_type(progress_color)
        )

        if tooltip_text:
            self.tooltip = ToolTip(self, tooltip_text, tooltip_waittime)

        self._draw()
