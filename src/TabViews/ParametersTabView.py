import Widgets.ThemedCtkWidgets as tcw
from Widgets.MultiParameterList import MultiParameterList
from Widgets.ParameterList import ParameterList
from Settings import Settings
from typing import List
import customtkinter as ctk
import tkinter


class ParametersTabView(tcw.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Add lists of parameters
        self.add_parameters_lists(row=0)

        # Add frame for buttons
        self.add_buttons(row=1)

    def add_parameters_lists(self, row):
        """
        Add parameter lists.

        Parameters:
            row (int): The row index to place the parameter lists.

        Description:
            This method initializes and adds a MultiParameterList.
            It specifies the directories for current and default YAML files for the list.
        """
        dir_yaml_current = Settings.current_device.files.parameters.path
        dir_yaml_default = Settings.current_device.files.parameters.path + "default/"
        self.parameter_lists = MultiParameterList(
            self, dir_yaml_default, dir_yaml_current
        )
        self.parameter_lists.grid(row=row, column=0, sticky="nesw")

    def add_buttons(self, row):
        """
        Add buttons to perform specific actions.

        Parameters:
            row (int): The row index to place the buttons frame.

        Description:
            This method adds a frame and configures it to contain buttons.
            Two buttons are added: one to save a copy of current parameters and another to revert parameters to default.
        """
        self.buttons_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.columnconfigure(0, weight=1)
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.grid(row=row, column=0, pady=(10, 0), sticky="nesw")

        # Add button to revert parameters to default
        self.button_revert = tcw.CTkButton(
            self.buttons_frame, text="Revert to default", command=self.revert_to_default
        )
        self.button_revert.grid(row=0, column=1, padx=(10, 0), pady=0, sticky="nes")
        self.revert_to_default_window: tcw.CTkToplevel = None

    def revert_to_default(self):
        if (
            self.revert_to_default_window is None
            or not self.revert_to_default_window.winfo_exists()
        ):
            self.revert_to_default_window = RevertToDefault(
                self, self.parameter_lists.parameter_lists
            )


class RevertToDefault(tcw.CTkToplevel):
    def __init__(self, master, parameter_lists: List[ParameterList]):
        """
        Lists the available parameter files, allowing to select which ones
        the user wishes to revert to default.

        Parameters:
            master: The parent widget.
            parameter_lists (List[ParameterList]): all the ParameterList that are going to be listed
        """
        super().__init__(master)
        self.title("Revert to Default")
        self.columnconfigure((0, 1), weight=1)
        self.rowconfigure((0, 1, 2), weight=1)

        self.parameter_lists = parameter_lists

        # Add display text
        self.display_text = tcw.CTkLabel(
            self,
            text="Select which files you wish to revert to the default values:",
            anchor="w",
        )
        self.display_text.grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 5), sticky="new"
        )

        # Add frame for the checkboxes
        self.parameters_frame = tcw.CTkFrame(self)
        self.parameters_frame.grid(
            row=1, column=0, columnspan=2, padx=20, pady=5, sticky="new"
        )

        # Add a checkbox for each parameter list (disable the ones that have
        # no changes wrt. the default)
        self.checkboxes: List[tcw.CTkCheckBox] = []
        for row, parameter_list in enumerate(parameter_lists, start=0):
            checkbox = tcw.CTkCheckBox(
                self.parameters_frame,
                text=parameter_list.title,
                state=(
                    tkinter.DISABLED
                    if parameter_list.is_equal_to_default()
                    else tkinter.NORMAL
                ),
            )
            checkbox.grid(row=row, column=0, padx=5, pady=5, sticky="new")
            self.checkboxes.append(checkbox)

        # Add revert button
        self.cancel_btn = tcw.CTkButton(
            self, text="Revert selected", command=self.revert_files
        )
        self.cancel_btn.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="sw")

        # Add cancel button
        self.cancel_btn = tcw.CTkButton(
            self, text="Cancel", command=self.destroy, font=ctk.CTkFont(weight="bold")
        )
        self.cancel_btn.grid(row=2, column=1, padx=20, pady=(5, 20), sticky="es")

        # Block parent window, forcing user to confirm/cancel first
        self.update_idletasks()
        self.grab_set()

    def revert_files(self):
        for checkbox in self.checkboxes:  # Loop through the checkboxes
            if checkbox._check_state:  # If the checkbox is selected
                # Find the ParameterList that matches the checkbox
                file_to_revert = next(
                    (
                        parameter_list
                        for parameter_list in self.parameter_lists
                        if parameter_list.title == checkbox._text
                    ),
                    None,
                )

                # Revert the file to default and reload it
                file_to_revert.revert_to_default()

        # Close the window
        self.destroy()
