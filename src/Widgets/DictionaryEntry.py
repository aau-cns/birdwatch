import Widgets.ThemedCtkWidgets as tcw
import customtkinter as ctk
import tkinter
from Settings import Settings
from typing import List
from LogManager import LogManager


class DictionaryEntry(tcw.CTkFrame):
    def __init__(
        self, master, current_value, default_value=None, command_on_update=None
    ):
        """
        Shows (recursively) a dictionary entry or value, which can be:
            - a single value
            - an array of values
            - a dictionary

        Parameters:
            master: The parent widget.
            current_value: The current value of entry
            default_value (optional): The default value of the entry
            command_on_update (optional): Function to run every time a value changes

        Example:
            dictionary_widget = DictionaryEntry(
                master,
                {
                    'key 1': 'value 1',
                    'sub-dictionary': {
                        'sub-key 1': 'sub-value 1',
                        'sub-key 2': 'sub-value 2'
                    }
                },
            )
        """
        super().__init__(master, fg_color="transparent")

        # Check if it is an array, a dictionary or a single value
        if isinstance(current_value, list):
            # Create a frame to hold all the values
            self.entries_frame = tcw.CTkFrame(self, fg_color="transparent")
            self.entries_frame.grid(row=1, column=0, padx=(20, 0), sticky="nw")

            self.entries: List[tcw.CTkFrame] = []
            self.labels: List[tcw.CTkLabel] = []
            self.parameters: List[DictionaryEntry] = []

            # Iterate over every element in the array
            for index, value in enumerate(current_value, start=0):
                # Create frame to place the label and the value
                entry = tcw.CTkFrame(self.entries_frame, fg_color="transparent")
                entry.grid(row=index, column=0, pady=2, sticky="nw")

                # Create bullet ("-") label
                label = tcw.CTkLabel(
                    entry,
                    text="-",
                    font=ctk.CTkFont(weight="bold"),
                    # Color the bullet if there is no default value for this index
                    text_color=(
                        Settings.current_device.color_theme.primary
                        if (default_value is None)
                        or (default_value.__len__() < index + 1)
                        else None
                    ),
                )
                label.grid(row=0, column=0, padx=(0, 5), sticky="nsw")

                # Add (recursively) the parameter
                try:
                    parameter = DictionaryEntry(
                        entry,
                        value,
                        default_value=(
                            default_value[index]
                            if (default_value is not None)
                            and (default_value.__len__() >= index + 1)
                            else None
                        ),
                        command_on_update=command_on_update,
                    )
                except Exception as e:
                    LogManager.error(f"An unexpected error occurred: {e}")
                parameter.grid(row=0, column=1, sticky="nsw")

                self.entries.append(entry)
                self.labels.append(label)
                self.parameters.append(parameter)

        elif isinstance(current_value, dict):
            # Create a frame to hold all the values
            self.entries_frame = tcw.CTkFrame(self, fg_color="transparent")
            self.entries_frame.grid(row=1, column=0, padx=(10, 0), sticky="nw")

            self.entries: List[tcw.CTkFrame] = []
            self.labels: List[tcw.CTkLabel] = []
            self.parameters: List[DictionaryEntry] = []

            # Iterate over every element in the array
            for row, (key, value) in enumerate(current_value.items(), start=0):
                # Create frame to place the label and the value
                entry = tcw.CTkFrame(self.entries_frame, fg_color="transparent")
                entry.grid(row=row, column=0, pady=2, sticky="nw")

                # Create label for the parameter name
                label = tcw.CTkLabel(
                    entry,
                    text=key + ":",
                    font=ctk.CTkFont(weight="bold"),
                    # Color the text if there is no key for this in the default values
                    text_color=(
                        Settings.current_device.color_theme.primary
                        if (default_value is None) or default_value.get(key) is None
                        else None
                    ),
                )
                label.grid(row=0, column=0, padx=(0, 5), sticky="nsw")

                # Add (recursively) the parameter
                parameter = DictionaryEntry(
                    entry,
                    value,
                    default_value=(
                        default_value.get(key) if default_value is not None else None
                    ),
                    command_on_update=command_on_update,
                )
                if isinstance(value, list) or isinstance(value, dict):
                    parameter.grid(row=1, column=0, padx=(10, 0), sticky="nsw")
                else:
                    parameter.grid(row=0, column=1, sticky="nsw")

                self.entries.append(entry)
                self.labels.append(label)
                self.parameters.append(parameter)

        else:
            # Create the variable to hold the value
            self.variable = tkinter.StringVar(value=current_value)
            self.variable_trace = self.variable.trace_add("write", self.on_value_change)
            self.command_on_update = command_on_update

            # Store default value
            self.default_value = default_value.__str__()

            # Create the entry for the value
            self.entry = tcw.CTkEntry(
                self,
                textvariable=self.variable,
                # If the value is different than the default, color it
                text_color=(
                    Settings.current_device.color_theme.primary
                    if default_value is None or default_value != current_value
                    else None
                ),
            )
            self.entry.grid(row=0, column=1, sticky="nw")

    def on_value_change(self, *args):
        """
        Function executed every time a value is edited.
        It changed the color of the value:
            - White: it is the same as the default file
            - Blue: it is not the same as the default file, or it doesn't exist on the default file
        """
        if self.default_value is not None:
            # Color according to if it matches the default value or not
            if self.default_value == self.variable.get():
                self.entry.configure(text_color="gray90")
            else:
                self.entry.configure(
                    text_color=Settings.current_device.color_theme.primary
                )

        # Execute the specified command
        if self.command_on_update is not None:
            self.command_on_update()

    def get_values(self):
        """
        Return the values recursively in the DictionaryEntry.
        If it is:
            - a single value: it simply returns the value
            - an list of entries: it returns a list of the result of calling this function on each entry
            - a dictionary: a dictionary matching each key with the result of calling this function on it
        """
        # Check if it has labels or is just the value
        if hasattr(self, "labels") and hasattr(self, "parameters"):

            # Check if it is a list or a dictionary
            if self.labels[0].cget("text") == "-":

                # Call this function on each element of the list
                list = []
                for parameter in self.parameters:
                    list.append(parameter.get_values())
                return list

            else:

                # Form a dictionary calling this function on each key of it
                dictionary = {}
                for label, parameter in zip(self.labels, self.parameters):
                    dictionary[label.cget("text").replace(":", "")] = (
                        parameter.get_values()
                    )

                return dictionary

        else:

            # Return the current value
            return self.variable.get()

    def is_equal_to_default(self):
        """
        Checks if all the current parameters match the default parameters

        Returns:
            - True: the current parameters are equal to the default
            - False: the current parameters are not equal to the default
        """

        # Check if it has labels or is just the value
        if hasattr(self, "labels") and hasattr(self, "parameters"):

            # If at least one of the elements is not equal to the
            # default, return False
            for parameter in self.parameters:
                if not parameter.is_equal_to_default():
                    return False
            return True

        else:

            # If the default value doesn't exist or it is not equal
            # to the current value, return False
            if (self.default_value is None) or (
                self.default_value != self.variable.get()
            ):
                return False
            else:
                return True
