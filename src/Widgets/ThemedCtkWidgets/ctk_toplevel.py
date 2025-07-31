import customtkinter as ctk
from .tooltip import ToolTipManager


class CTkToplevel(ctk.CTkToplevel):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        # Set it so that all windows are grouped under the root window
        self.wm_group(".")

        # Close the window when the escape key is pressed
        self.bind("<Escape>", lambda event: self.close())

        # Hide all active tooltips when this window is opened
        ToolTipManager.hide_all()

        # Block parent window, forcing user to close this window first
        self.update_idletasks()
        self.grab_set()

    def close(self):
        self.destroy()
