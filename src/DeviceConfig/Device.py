from DeviceConfig.SSHConfig import SSHConfig
from DeviceConfig.ColorTheme import ColorTheme
from from_root import from_root
from LogManager import LogManager
import enum
import re
from getpass import getuser


class Files:
    class Path:
        class Type(enum.Enum):
            FILE = 0
            DIRECTORY = 1

        class Scope(enum.Enum):
            IN_WORKSPACE = 0
            GLOBAL = 1

        def __init__(self, path: str, user: str, workspace_path: str, type: Type):
            """
            Represents a path to a file or directory.

            Parameters:
                path (str): The path to the file or directory.
                user (str): The user of the device.
                workspace_path (str): The path to the workspace.
                type (Type): The type of the path (file or directory).
            """
            self.type = type

            # Check if the path is a file or a directory
            if type == Files.Path.Type.FILE:
                # Check if the path has a valid extension
                if not re.match(r".*\.[a-zA-Z0-9]+$", path):
                    raise ValueError("File path must end with a valid extension")
            else:
                # Check if the path ends with a slash
                if not path.endswith("/"):
                    path += "/"

            # Check if the path is in the workspace or global
            if path.startswith("~/"):
                self.scope = Files.Path.Scope.GLOBAL
                self.path = path.replace("~/", f"/home/{user}/")
            elif path.startswith(f"home/{user}/"):
                self.scope = Files.Path.Scope.GLOBAL
                self.path = "/" + path
            elif path.startswith(f"/home/{user}/"):
                self.scope = Files.Path.Scope.GLOBAL
                self.path = path
            else:
                self.scope = Files.Path.Scope.IN_WORKSPACE

                if path.startswith("/"):
                    path = path[1:]
                self.path = workspace_path + path

        def get_path(self, user: str, workspace_path: str) -> str:
            """
            Get the path to the file or directory.
            """
            if self.scope == Files.Path.Scope.GLOBAL:
                return self.path.replace(f"/home/{user}/", "~/")
            else:
                return self.path.replace(workspace_path, "")

        def __str__(self):
            return self.path

    def __init__(self, user: str):
        self.user = user

        self.workspace_path: str = None
        self.source: Files.Path = None
        self.nodes: Files.Path = None
        self.topics: Files.Path = None
        self.recordings: Files.Path = None
        self.missions: Files.Path = None
        self.parameters: Files.Path = None

    def load_workspace_path(self, workspace_path: str):
        """
        Load the workspace path.
        """

        # Check if the workspace path ends with a slash
        if not workspace_path.endswith("/"):
            workspace_path += "/"

        # Check if the workspace path is in the global or user's home directory
        if workspace_path.startswith("~/"):
            self.workspace_path = workspace_path.replace("~/", f"/home/{self.user}/")
        elif workspace_path.startswith(f"home/{self.user}/"):
            self.workspace_path = "/" + workspace_path
        elif workspace_path.startswith(f"/home/{self.user}/"):
            self.workspace_path = workspace_path
        else:
            raise ValueError("Workspace path must start with ~/ or /home/<user>/")

    def load_path(self, path: str, type: Path.Type):
        """
        Load a file or directory path.
        """
        if path is not None:
            return Files.Path(path, self.user, self.workspace_path, type)

    def get_workspace_path(self, user: str) -> str:
        """
        Get the workspace path.
        """
        return self.workspace_path.replace(f"/home/{user}/", "~/")

    def to_dictionary(self) -> dict:
        """
        Convert the files configuration to a dictionary.
        """
        files_dict = {}

        files_dict["workspace_path"] = self.get_workspace_path(self.user)

        if self.source is not None:
            files_dict["source"] = self.source.get_path(self.user, self.workspace_path)

        if self.nodes is not None:
            files_dict["nodes"] = self.nodes.get_path(self.user, self.workspace_path)

        if self.topics is not None:
            files_dict["topics"] = self.topics.get_path(self.user, self.workspace_path)

        if self.recordings is not None:
            files_dict["recordings"] = self.recordings.get_path(
                self.user, self.workspace_path
            )

        if self.missions is not None:
            files_dict["missions"] = self.missions.get_path(
                self.user, self.workspace_path
            )

        if self.parameters is not None:
            files_dict["parameters"] = self.parameters.get_path(
                self.user, self.workspace_path
            )

        return files_dict


class Device:
    """
    Represents a device with configuration parameters.

    Args:
        config_params (dict): A dictionary containing configuration parameters
            for the device.

    Raises:
        KeyError: If the one of the expected parameters is missing in the device configuration.
    """

    def __init__(self, name: str, config_params: dict):

        self.name = name

        # Check if all required fields are present in the configuration
        missing_field = self.check_required_fields(config_params)
        if missing_field is not None:
            raise KeyError(f'Required field "{missing_field}" not found in file')

        # If there is a configuration for SSH connections in the config_params
        if "ssh_connection" in config_params:
            try:
                # Store username of target device
                self.ssh_config = SSHConfig(config_params["ssh_connection"]["username"])

                # Store all possible IPs of the target device in the different networks
                for connection in config_params["ssh_connection"]["networks"]:
                    try:
                        self.ssh_config.add_network(
                            connection["name"], connection["ip"]
                        )
                    except ValueError as e:
                        LogManager.error(f"Could not add network to {self.name}: {e}")

                if "selected_network" in config_params["ssh_connection"]:
                    try:
                        self.ssh_config.select_network(
                            config_params["ssh_connection"]["selected_network"]
                        )
                    except Exception as e:
                        raise e
            except KeyError as e:
                raise KeyError(
                    f"Device configuration is missing required parameter {e}."
                )
        else:
            self.ssh_config = None

        # Add files configuration
        try:
            self.files = Files(
                user=self.ssh_config.username if self.ssh_config else getuser()
            )

            self.files.load_workspace_path(config_params["files"]["workspace_path"])

            if "source" in config_params["files"]:
                self.files.source = self.files.load_path(
                    config_params["files"]["source"], Files.Path.Type.FILE
                )

            self.files.nodes = self.files.load_path(
                config_params["files"]["nodes"], Files.Path.Type.FILE
            )

            self.files.topics = self.files.load_path(
                config_params["files"]["topics"], Files.Path.Type.FILE
            )

            self.files.recordings = self.files.load_path(
                config_params["files"]["recordings"], Files.Path.Type.DIRECTORY
            )

            self.files.missions = self.files.load_path(
                config_params["files"]["missions"], Files.Path.Type.DIRECTORY
            )

            self.files.parameters = self.files.load_path(
                config_params["files"]["parameters"], Files.Path.Type.DIRECTORY
            )
        except KeyError as e:
            raise KeyError(f"Device configuration is missing required parameter {e}.")
        except ValueError as e:
            raise ValueError(f"Device configuration has an invalid parameter {e}.")

        # If there is a configuration for a color theme in the config_params
        if "color_theme" in config_params:
            try:
                self.color_theme = ColorTheme(
                    config_params["color_theme"]["primary"],
                    config_params["color_theme"]["dark_primary"],
                    config_params["color_theme"]["darker_primary"],
                )
            except KeyError as e:
                raise KeyError(
                    f"Device configuration is missing required parameter {e}."
                )
        else:
            self.color_theme = ColorTheme()

        # If there is a configuration for an app icon in the config_params
        if "app_icon_path" in config_params:
            if config_params["app_icon_path"].startswith("/"):
                config_params["app_icon_path"] = config_params["app_icon_path"][1:]
            self.app_icon_path = str(from_root(config_params["app_icon_path"]))
        else:
            self.app_icon_path = None

    def load_file_field(
        self, config_files: dict, desired_field: str, workspace_path: str
    ) -> str:
        """
        Load a file field from the configuration files.
        """

        # Check if the field is present in the configuration files
        if desired_field in config_files:
            return workspace_path + config_files[desired_field]

        # Check if the field is present in the configuration files with the "_global" suffix
        elif (desired_field + "_global") in config_files:
            return config_files[desired_field + "_global"]
        else:
            return ""

    def check_required_fields(self, config_params: dict):
        # Check all expected file configuration fields
        if "files" not in config_params:
            return "files"
        elif "workspace_path" not in config_params["files"]:
            return "workspace_path"
        elif (
            "nodes" not in config_params["files"]
            and "nodes_global" not in config_params["files"]
        ):
            return "nodes"
        elif (
            "topics" not in config_params["files"]
            and "topics_global" not in config_params["files"]
        ):
            return "topics"
        elif (
            "recordings" not in config_params["files"]
            and "recordings_global" not in config_params["files"]
        ):
            return "recordings_global"
        elif (
            "parameters" not in config_params["files"]
            and "parameters_global" not in config_params["files"]
        ):
            return "parameters"

        # Check all required fields related to the SSH Connection (if an SSH connection is specified)
        elif ("ssh_connection" in config_params) and (
            "username" not in config_params["ssh_connection"]
        ):
            return "ssh_connection/username"
        elif ("ssh_connection" in config_params) and (
            "networks" not in config_params["ssh_connection"]
        ):
            return "ssh_connection/networks"

        # Check all required fields related to the color theme (if a color theme is specified)
        elif ("color_theme" in config_params) and (
            "primary" not in config_params["color_theme"]
        ):
            return "color_theme/primary"
        elif ("color_theme" in config_params) and (
            "dark_primary" not in config_params["color_theme"]
        ):
            return "color_theme/dark_primary"
        elif ("color_theme" in config_params) and (
            "darker_primary" not in config_params["color_theme"]
        ):
            return "color_theme/darker_primary"

        # All required fields where present
        else:
            return None

    def to_dictionary(self) -> dict:
        """
        Convert the device configuration to a dictionary.
        """
        device_dict = {}

        # Add SSH configuration
        if self.ssh_config is not None:
            device_dict["ssh_connection"] = self.ssh_config.to_dictionary()

        # Add files configuration
        device_dict["files"] = self.files.to_dictionary()

        # Add color theme configuration
        if self.color_theme is not None and not self.color_theme.is_default():
            device_dict["color_theme"] = self.color_theme.to_dictionary()

        # Add app icon path
        if self.app_icon_path is not None:
            device_dict["app_icon_path"] = self.app_icon_path[
                len(str(from_root(""))) + 1 :
            ]

        return device_dict
