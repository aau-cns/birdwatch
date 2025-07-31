import Widgets.ThemedCtkWidgets as tcw


class MessageWindow(tcw.CTkToplevel):
    def __init__(
        self,
        master,
        message: str,
        title: str = "Message",
        button_text: str = "Close",
    ):
        """
        Initialize a message window.

        Parameters:
            master: The parent widget.
            message (str): The message to display in the window.
            title (str, optional): The title of the window.
            button_text (str, optional): Text to display on the close button.

        Description:
            This class creates a message window that displays a message.

        Example:
            message_window = None

            def create_message_window():
                if message_window is None or not message_window.winfo_exists():
                    message_window = MessageWindow(
                        master,
                        "There are unsaved changes. Please save or discard before proceeding",
                        title = "Unsaved changes"
                    )
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

        # Add "Close" button
        self.cancel_btn = tcw.CTkButton(self, text=button_text, command=self.close)
        self.cancel_btn.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="es")

        self.bind("<Return>", lambda event: self.close)
        self.bind("<KP_Enter>", lambda event: self.close)

    def close(self):
        self.destroy()
