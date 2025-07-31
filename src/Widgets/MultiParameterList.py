import Widgets.ThemedCtkWidgets as tcw
from ShellCommands import ShellCommands as sh
from typing import List
from Settings import Settings
from Widgets.ParameterList import ParameterList


class MultiParameterList(tcw.CTkScrollableFrame):
    def __init__(self, master, path_default, path_current, expand=True):
        """
        Initialize a scrollable frame containing multiple parameter lists.

        Parameters:
            master: The parent widget.
            expand (bool): Whether to expand each ParameterList initially. Default = True.

        Description:
            This class creates a scrollable frame to display multiple parameter lists.
            It loads YAML files from the provided paths, compares them, and displays the differences.
        """
        super().__init__(master)
        self.columnconfigure(0, weight=1)

        # Verify if path_default exists, if not, create it
        if (
            not sh.execute(
                f"test -d {path_default} && echo 'exists' || echo 'not exists'"
            ).strip()
            == "exists"
        ):
            sh.execute(f"mkdir -p {path_default}")

        # Get list of YAML files in the current and default directories
        try:
            current_files = sh.execute(f"ls {path_current}*.yaml").splitlines()
            current_files = [
                file.split("/")[-1].replace(
                    ".yaml", ""
                )  # Keep only the file name without the path and extension
                for file in current_files
            ]
        except:
            current_files = []

        try:
            default_files = sh.execute(f"ls {path_default}*.yaml").splitlines()
            default_files = [
                file.split("/")[-1].replace(
                    ".yaml", ""
                )  # Keep only the file name without the path and extension
                for file in default_files
            ]
        except:
            default_files = []

        # If no files are found in either directory, display a message
        if len(current_files) == 0 and len(default_files) == 0:
            self.unavailable_params_label = tcw.CTkLabel(
                self, text="No parameters available."
            )
            self.unavailable_params_label.grid(row=0, column=0)
            return

        # Create copy of the default files that don't currently have a matching current file
        for file in default_files:
            if file not in current_files:
                sh.execute(f"cp {path_default}/{file}.yaml {path_current}/{file}.yaml")
                current_files.append(file)

        # Create copy of the current files that don't currently have a matching default file
        for file in current_files:
            if file not in default_files:
                sh.execute(f"cp {path_current}/{file}.yaml {path_default}/{file}.yaml")
                default_files.append(file)

        # Create empty list of ParameterList
        self.parameter_lists: List[ParameterList] = []

        # Loop through all the files in path_current
        current_files.sort()
        for file_count, current_file in enumerate(current_files, start=1):
            parameters = ParameterList(
                self,
                current_file,
                expand=expand,
            )

            parameters.grid(row=file_count - 1, column=0, padx=5, pady=10, sticky="new")
            self.parameter_lists.append(parameters)
