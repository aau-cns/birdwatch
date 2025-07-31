from .LoggingTextbox import LoggingTextbox
import Widgets.ThemedCtkWidgets as tcw
from Settings import Settings


class CollapsibleLoggingTextbox(tcw.CTkFrame):
    __show_logs_text = "▶ Show logs"
    __hide_logs_text = "▼ Hide logs"

    __logs_visible = False

    message_count = 0

    def __init__(self, master, fg_color="transparent", *args, **kwargs):
        """
        Initialize the CollapsibleLoggingTextbox.

        Parameters:
            master: The parent widget.
        """
        super().__init__(master, fg_color=fg_color, *args, **kwargs)
        self.columnconfigure(0, weight=1)

        # Create the frame for the show/hide labels
        self.labels_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.labels_frame.grid(row=0, column=0, sticky="new")

        # Create the label for showing/hiding the logs
        self.label = tcw.CTkLabel(self.labels_frame, text=self.__hide_logs_text)
        self.label.grid(row=0, column=0, sticky="nw")
        self.label.bind("<Button-1>", self.toggle_logging_textbox)

        # Create the label for showing the number of new messages
        self.new_messages_label = tcw.CTkLabel(self.labels_frame, text="")

        # Create the LoggingTextbox
        self.logging_textbox = LoggingTextbox(self)
        self.toggle_logging_textbox()

        # Bind the update_message_count method to be called when the message_count variable changes
        self.logging_textbox.message_count.trace_add("write", self.update_message_count)

    def toggle_logging_textbox(self, event=None):
        """
        Toggle the visibility of the LoggingTextbox.
        """
        if self.__logs_visible:
            self.logging_textbox.grid_remove()  # Hide the LoggingTextbox
            self.label.configure(text=self.__show_logs_text)  # Change the label text
            self.__logs_visible = False
        else:
            self.logging_textbox.grid(
                row=1, column=0, columnspan=2, pady=(5, 0), sticky="nesw"
            )  # Show the LoggingTextbox
            self.label.configure(text=self.__hide_logs_text)  # Change the label text
            self.new_messages_label.grid_remove()  # Hide the new messages label
            self.__logs_visible = True

    def update_message_count(self, *args):
        """
        Update the message count.
        """
        if not self.__logs_visible:
            # Update the new messages label
            self.new_messages_label.configure(
                text=f"({self.logging_textbox.message_count.get()-self.message_count} unseen {'messages' if self.logging_textbox.message_count.get()-self.message_count > 1 else 'message'})"
            )

            # Set the text color based on the current device color theme
            if Settings.current_device is not None:
                self.new_messages_label.configure(
                    text_color=Settings.current_device.color_theme.primary
                )

            # Show the new messages label
            self.new_messages_label.grid(row=0, column=1, padx=(5, 0), sticky="nw")
        else:
            # Update the message count
            self.message_count = self.logging_textbox.message_count.get()
