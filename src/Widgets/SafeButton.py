import Widgets.ThemedCtkWidgets as tcw
from typing import Union, Callable, Any, Optional
import tkinter
from Settings import Settings


class SafeButton(tcw.CTkFrame):
    def __init__(
        self,
        master,
        text: str,
        command: Union[Callable[[], Any], None],
        threshold: float = 95,
        timeout: float = None,
        slider_width: Optional[int] = None,
        button_width: Optional[int] = None,
        slider_tooltip: Optional[str] = None,
        btn_tooltip: Optional[str] = None,
    ):
        """
        Creates a widget that is a slider and a button. The button is only enabled
        when the slider is all the way to the right, and it is disabled again after
        pressing the button

        Parameters:
            master: the parent widget
            text (string): the text to show in the button
            command (callable): function to run when the button is pressed
            threshold (optional, float): percentage of the slider it needs to be
                in order to enable the button. Default: 95
            timeout (optional, float): number of seconds after which the button
                will be disabled and the slider reset to zero if the button has not
                been pressed after enabling it. Default: no timeout
            slider_width (optional, int): width of the slider. Default: 200
            button_width (optional, int): width of the button. Default: 140
            slider_tooltip (optional, string): text to show in the tooltip of the slider when it is disabled
            btn_tooltip (optional, string): text to show in the tooltip of the button when it is enabled
        """
        super().__init__(master, fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Add slider
        self.slider = tcw.CTkSlider(
            self,
            from_=0,
            to=100,
            command=self.toggle_button,
            tooltip_text=(
                "Slide to the right to enable the button",
                slider_tooltip if slider_tooltip is not None else "",
            ),
        )
        self.slider.set(0)
        if slider_width is not None:
            self.configure(width=slider_width)
        self.slider.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.threshold = threshold

        self.command = command
        self.button = tcw.CTkButton(
            self,
            text=text,
            state=tkinter.DISABLED,
            command=self.execute,
            tooltip_text=(
                btn_tooltip if btn_tooltip is not None else "",
                "Slide to the right to enable the button",
            ),
        )
        if button_width is not None:
            self.configure(width=button_width)
        self.button.grid(row=0, column=1, sticky="e")

        self.timeout = timeout
        self.after_id = None

    def execute(self):
        """
        Executes the specified command, disables the button and
        resets the slider
        """
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.command()
        self.disable()

    def toggle_button(self, value):
        """
        Checks if the slider is above the specified threshold. If
        it is, it enables the button and (if a timeout was specified)
        sets a delayed call to disable the button again
        """
        if value > self.threshold:
            if self.button.cget("state") == tkinter.DISABLED:
                if self.timeout is not None:
                    self.after_id = self.after(self.timeout * 1000, self.disable)
                self.button.configure(state=tkinter.NORMAL)
        else:
            self.button.configure(state=tkinter.DISABLED)

    def disable(self):
        """
        Disables the button and resets the slider
        """
        self.slider.set(0)
        self.button.configure(state=tkinter.DISABLED)

    def slider_disable(self):
        """
        Disables the slider
        """
        self.disable()
        self.slider.configure(state=tkinter.DISABLED)
        self.slider.configure(button_color="grey50")

    def slider_enable(self):
        """
        Enables the slider
        """
        self.slider.configure(state=tkinter.NORMAL)
        self.slider.configure(button_color=Settings.current_device.color_theme.primary)
