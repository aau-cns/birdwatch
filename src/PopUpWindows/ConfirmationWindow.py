import Widgets.ThemedCtkWidgets as tcw
from typing import Union, Callable, Any
import customtkinter as ctk


class ConfirmationWindow(tcw.CTkToplevel):
    def __init__(
        self,
        master,
        message: str,
        confirm_command: Union[Callable[[], Any], None],
        cancel_command: Union[Callable[[], Any], None] = None,
        title: str = "Confirmation",
    ):
        """
        Initialize a confirmation window.

        Parameters:
            master: The parent widget.
            message (str): The message to display in the window.
            confirm_command (Callable): The function to call when confirm button is clicked.
            cancel_command (Callable, optional): The function to call when cancel button is clicked.
            title (str, optional): The title of the window.

        Description:
            This class creates a confirmation window with a message and confirm/cancel buttons.
            It executes specified commands when confirm or cancel button is clicked.

        Example:
            confirm_window = None

            def create_confirm_window():
                if confirm_window is None or not confirm_window.winfo_exists():
                    confirm_window = ConfirmationWindow(
                        master,
                        "Are you sure you want to proceed?",
                        confirm_command=handle_confirm
                    )

            def handle_confirm(self):
                # Handle confirmation
        """
        super().__init__(master)

        # Configure window
        self.window_title = title
        self.title(self.window_title)
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1), weight=1)

        # Add text
        self.label = tcw.CTkLabel(self, text=message)
        self.label.grid(row=0, column=0, padx=20, pady=20, columnspan=2)

        # Add "Confirm" button
        self.confirm_command = confirm_command
        self.confirm_btn = tcw.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_btn.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="sw")

        # Add "Cancel" button
        self.cancel_command = cancel_command
        self.cancel_btn = tcw.CTkButton(
            self, text="Cancel", command=self.cancel, font=ctk.CTkFont(weight="bold")
        )
        self.cancel_btn.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="es")

        self.bind("<Return>", lambda event: self.confirm())
        self.bind("<KP_Enter>", lambda event: self.confirm())
        self.bind("<Escape>", lambda event: self.cancel())

    def confirm(self):
        self.confirm_command()
        self.destroy()

    def cancel(self):
        if self.cancel_command is not None:
            self.cancel_command()
        self.destroy()
