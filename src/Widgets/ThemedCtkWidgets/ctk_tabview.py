from Settings import Settings
import customtkinter as ctk
from typing import Union, Tuple, Callable, Optional, Any


class CTkTabview(ctk.CTkTabview):
    def __init__(
        self,
        master: Any,
        width: int = 300,
        height: int = 250,
        corner_radius: Optional[int] = None,
        border_width: Optional[int] = None,
        bg_color: Union[str, Tuple[str, str]] = "transparent",
        fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        border_color: Optional[Union[str, Tuple[str, str]]] = None,
        segmented_button_fg_color: Optional[Union[str, Tuple[str, str]]] = None,
        segmented_button_selected_color: Optional[Union[str, Tuple[str, str]]] = None,
        segmented_button_selected_hover_color: Optional[
            Union[str, Tuple[str, str]]
        ] = None,
        segmented_button_unselected_color: Optional[Union[str, Tuple[str, str]]] = None,
        segmented_button_unselected_hover_color: Optional[
            Union[str, Tuple[str, str]]
        ] = None,
        text_color: Optional[Union[str, Tuple[str, str]]] = None,
        text_color_disabled: Optional[Union[str, Tuple[str, str]]] = None,
        command: Union[Callable, Any] = None,
        anchor: str = "center",
        state: str = "normal",
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
            segmented_button_fg_color=segmented_button_fg_color,
            segmented_button_selected_color=segmented_button_selected_color,
            segmented_button_selected_hover_color=segmented_button_selected_hover_color,
            segmented_button_unselected_color=segmented_button_unselected_color,
            segmented_button_unselected_hover_color=segmented_button_unselected_hover_color,
            text_color=text_color,
            text_color_disabled=text_color_disabled,
            state=state,
            command=command,
            anchor=anchor,
            **kwargs,
        )

        if (
            segmented_button_selected_color is None
            and Settings.current_device is not None
        ):
            self.configure(
                segmented_button_selected_color=Settings.current_device.color_theme.primary
            )

        if (
            segmented_button_selected_hover_color is None
            and Settings.current_device is not None
        ):
            self.configure(
                segmented_button_selected_hover_color=Settings.current_device.color_theme.dark_primary
            )
