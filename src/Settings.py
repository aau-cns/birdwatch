import socket
from typing import List

import yaml
from from_root import from_root

from DeviceConfig.Device import Device
from DeviceConfig.Network import Network
from LogManager import LogManager


class Settings:
    __config_file_path = from_root("config/config.yaml")
    __target_devices_folder = from_root("config/target_devices/")

    default_rviz1_config_file = from_root("config/default_rviz1.rviz")
    default_rviz2_config_file = from_root("config/default_rviz2.rviz")

    missions_folder = from_root("missions/")

    current_device: Device = None
    current_network: Network = None
    target_devices: List[Device] = []
    local_ip: str = None

    root_app = None

    @classmethod
    def set_paths(cls, config_file_path: str = None, target_device_folder: str = None):
        if config_file_path:
            cls.__config_file_path = from_root(config_file_path)
        if target_device_folder:
            cls.__target_devices_folder = from_root(target_device_folder)

    @classmethod
    def load_devices(cls):
        """
        Load configurations for possible target devices from YAML files located in the
        specified directory.

        This function iterates through YAML files in the 'config/target_devices' directory,
        excluding 'template.yaml'. For each valid file, it loads the device configuration,
        creates a Device object, and appends it to the 'target_devices' list attribute.
        """
        device_files = [
            file
            for file in cls.__target_devices_folder.iterdir()
            if file.is_file() and file.suffix == ".yaml"
        ]

        # global target_devices
        cls.target_devices = []

        for device_file in device_files:
            if device_file.stem != "Template":
                device_path = cls.__target_devices_folder.joinpath(device_file)

                try:
                    with device_path.open("r") as device_file_obj:
                        device = Device(
                            device_file.stem,
                            yaml.safe_load(device_file_obj),
                        )

                    cls.target_devices.append(device)
                except KeyError as e:
                    LogManager.warning(f"Skipping {device_file}: {e}")
                except Exception as e:
                    LogManager.error(f"Error loading {device_file}: {e}")

    @classmethod
    def load_config(cls):
        """
        Load configurations from the 'config/config.yaml' file.
        """
        with cls.__config_file_path.open("r") as config_file_obj:
            configData = yaml.safe_load(config_file_obj)

        # Load path to QGroundControl
        if "qgroundcontrol" in configData:
            cls.qgroundcontrol = configData["qgroundcontrol"]
        else:
            cls.qgroundcontrol = None

    @classmethod
    def get_local_ip(cls) -> str:
        """
        Get the local IP address used to connect to the target device.
        """
        # Create a UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Try to stablish a connection to the target device
            s.connect((cls.current_network.ip, 1))

            # Get the local IP address used to connect to the target device
            ip = s.getsockname()[0]
        except Exception:
            # Default to localhost if the connection fails
            ip = "localhost"
        finally:
            # Close the socket
            s.close()
        return ip

    @classmethod
    def set_current_device(cls, device_name: str, network_name: str = None) -> bool:
        """
        Set the current device to the one with the specified name.
        """
        # Find the device with the specified name
        new_device = next(
            (Device for Device in cls.target_devices if Device.name == device_name),
            None,
        )

        # If the device was found, set it as the current device
        if new_device != None:
            cls.current_device = new_device

            # Set the current network
            if new_device.ssh_config != None and new_device.ssh_config.networks != []:

                # If a network name was specified, set it as the current network
                if network_name is not None:
                    network_index = new_device.ssh_config.get_network_index(
                        network_name
                    )

                    # If the network name was not found, default to the last used network
                    if network_index is None:
                        LogManager.error(
                            f"Network {network_name} not found in list of available networks for {device_name}, defaulting to last used network"
                        )
                        network_index = new_device.ssh_config.selected_network
                    cls.set_current_network(network_index)
                else:
                    cls.set_current_network(new_device.ssh_config.selected_network)
            else:
                LogManager.info(
                    "No specified (or incorrect) SSH configuration. Will run commands locally"
                )
                cls.set_current_network(None)

            # Set the app icon
            if cls.root_app:
                cls.root_app.set_icon(new_device.app_icon_path)

            return True
        else:
            return False

    @classmethod
    def set_current_network(cls, network_index):
        """
        Set the current network to the one with the specified index.
        """
        if network_index is None:
            cls.current_network = None
            cls.local_ip = "localhost"
        else:
            cls.current_network = cls.current_device.ssh_config.networks[network_index]
            cls.current_device.ssh_config.selected_network = network_index
            cls.local_ip = cls.get_local_ip()

    @classmethod
    def save_device(cls, device: Device):
        """
        Save the configuration of the specified device to a YAML file.
        """
        device_path = cls.__target_devices_folder.joinpath(f"{device.name}.yaml")

        with device_path.open("w") as device_file_obj:
            yaml.safe_dump(device.to_dictionary(), device_file_obj, sort_keys=False)

    @classmethod
    def is_ssh_config_set(cls):
        """
        Check if an SSH configuration is set for the current device.
        """
        if (cls.current_device is not None) and (
            cls.current_device.ssh_config is not None
        ):
            return True
        else:
            return False

    @classmethod
    def set_root_app(cls, root_app):
        cls.root_app = root_app
