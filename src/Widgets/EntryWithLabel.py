import Widgets.ThemedCtkWidgets as tcw
import tkinter
from typing import Optional


class EntryWithLabel(tcw.CTkFrame):

    def __init__(
        self,
        master,
        label: str,
        placeholder_text: str = "",
        tooltip: Optional[str] = None,
    ):
        """
        Initialize a custom frame containing a label and an entry field.

        This class inherits from customtkinter.CTkFrame.

        Parameters:
            master: The parent widget.
            label (str): The label text.
            placeholder_text (str): The placeholder text for the entry field.

        Description:
            This class creates an entry field with an associated label.
            The label and entry field are arranged horizontally within the frame.
        """
        super().__init__(master)
        self.configure(fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.label = tcw.CTkLabel(
            self,
            text=label,
            width=0,
            anchor="w",
            tooltip_text=tooltip,
        )
        self.label.grid(row=0, column=0, padx=(0, 10), sticky="new")

        self.textvar = tkinter.StringVar(value=placeholder_text)
        self.entry = tcw.CTkEntry(
            self,
            textvariable=self.textvar,
            tooltip_text=tooltip,
        )
        self.entry.grid(row=0, column=1, sticky="new")

    def get(self) -> str:
        """
        Get the text in the entry field.

        Returns:
            str: The text in the entry field.
        """
        return self.textvar.get()

    def set(self, text: str):
        """
        Set the text in the entry field.

        Parameters:
            text (str): The text to set in the entry field.
        """
        self.textvar.set(text)
