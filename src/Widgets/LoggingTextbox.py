import customtkinter as ctk
import tkinter
from enum import Enum


class LoggingTextbox(ctk.CTkTextbox):
    class LogLevels(Enum):
        """
        Enum for the different levels of logging
        """

        INFO = "info"
        WARNING = "warning"
        ERROR = "error"

    message_count: tkinter.IntVar = None

    def __init__(self, master, **kwargs):
        """
        Initialize the LoggingTextbox.

        Parameters:
            master: The parent widget.
        """
        super().__init__(master, wrap="word", state="disabled", **kwargs)

        # Configure the tags
        self.tag_config(self.LogLevels.INFO.value, foreground="white")
        self.tag_config(self.LogLevels.WARNING.value, foreground="yellow")
        self.tag_config(self.LogLevels.ERROR.value, foreground="red")

        self.message_count = tkinter.IntVar(value=0)

    def add_line(self, text: str, level: LogLevels = LogLevels.INFO):
        """
        Adds a line of text

        Parameters:
            text (string): text to show
            level (optional, LogLevels): the severity level
        """
        self.configure(state="normal")  # Enable the textbox
        self.insert("end", text + "\n", level.value)  # Add the text
        self.yview_moveto(1.0)  # Scroll to the bottom
        self.configure(state="disabled")  # Disable the textbox
        self.message_count.set(
            self.message_count.get() + 1
        )  # Increment the message count
