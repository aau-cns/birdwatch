import yaml
from FileManager import FileManager as fm
from Settings import Settings
from Widgets.CollapsibleFrame import CollapsibleFrame
from Widgets.DictionaryEntry import DictionaryEntry
from typing import Union, Tuple, Optional
from LogManager import LogManager


class ParameterList(CollapsibleFrame):
    def __init__(
        self,
        master,
        title: str,
        fg_color: Optional[Union[str, Tuple[str, str]]] = "transparent",
        border_color: Optional[Union[str, Tuple[str, str]]] = "gray50",
        expand: bool = True,
    ):
        """
        Loads a parameter yaml file and creates a CollapsableFrame widget with the
        file name as its title and display the parameters, comparing it to the
        corresponding default parameter file

        Parameters:
            master: The parent widget.
            title (string): name of the file and title of the frame
            fg_color (optional): Background color of the frame
            border_color (optional): Color of the border of the frame
            expand (optional, boolean): If True, the frame will appear expanded, if False, it will appear collapsed

        Example:
            parameter_list = ParameterList(
                master,
                "example_parameters",
                expand = True,
            )
        """
        super().__init__(
            master, title=title, fg_color=fg_color, border_color=border_color
        )

        self.title = title

        # Load current file
        try:
            self.current_values = yaml.safe_load(
                fm.read_file(
                    Settings.current_device.files.parameters.path + title + ".yaml"
                )
            )
        except Exception as e:
            raise e

        # Load default file (if it exists)
        try:
            default_values = yaml.safe_load(
                fm.read_file(
                    Settings.current_device.files.parameters.path
                    + "default/"
                    + title
                    + ".yaml"
                )
            )
        except:
            default_values = None

        self.set_subwidget(
            DictionaryEntry(
                self,
                self.current_values,
                default_value=default_values,
                command_on_update=self.update_file,
            ),
            expand=expand,
        )

    def update_file(self):
        """
        Updates the current file based on the current values
        """
        try:
            fm.write_file(
                Settings.current_device.files.parameters.path + self.title + ".yaml",
                yaml.dump(self.subwidget.get_values(), sort_keys=False),
            )
        except Exception as e:
            # TODO: Add a popup to show the error
            LogManager.error(f"Could not update parameter file {self.title}.yaml: {e}")

    def revert_to_default(self):
        """
        Overwrites the current file with the default file, and reloads the widget
        """
        default_path = (
            Settings.current_device.files.parameters.path
            + "default/"
            + self.title
            + ".yaml"
        )
        current_path = (
            Settings.current_device.files.parameters.path + self.title + ".yaml"
        )
        try:
            fm.copy_file(default_path, current_path)
        except Exception as e:
            raise e

        LogManager.info(f"Parameter file {self.title}.yaml reverted to default")
        self.refresh()

    def refresh(self):
        """
        Destroys and forms the widget again
        """
        master = self.master
        title = self.title
        fg_color = self._fg_color
        border_color = self._border_color
        grid_info = self.grid_info()
        self.destroy()
        self.__init__(master, title, fg_color=fg_color, border_color=border_color)
        if grid_info:
            self.grid(**grid_info)

    def is_equal_to_default(self):
        """
        Checks if all the current parameters match the default parameters

        Returns:
            - True: the current parameters are equal to the default
            - False: the current parameters are not equal to the default
        """
        return self.subwidget.is_equal_to_default()
