#!/usr/bin/env python
import argparse
from typing import List

import yaml

from FileManager import FileManager as fm
from LogManager import LogManager
from Settings import Settings
from ShellCommands import ShellCommands as sh
from ShellCommands import TmuxPaneCommand


class NodeEntryStruct:
    row: int
    name: str
    order: int
    delay_ms: int = 0
    window = None,
    run: bool = True

    def __init__(
        self,
        row: int,
        name: str,
        order: int,
        delay_ms: int = 0,
        window: str=None,
        run: bool = True,
    ):
        self.row = row
        self.name = name
        self.order = order
        self.delay_ms = delay_ms
        self.window = window
        self.run = run


class BirdWatchCli:
    @classmethod
    def __init__(self, target_device: str, network_name: str,
                 config_file_path: str = None, target_device_folder: str = None):
        self.nodes_config = []
        # Initialize logger
        LogManager.init()

        # Load settings from config
        Settings.set_paths(config_file_path, target_device_folder)

        # Load settings from config
        Settings.load_config()
        Settings.load_devices()
        if target_device is not None:
            # Set the selected device
            if Settings.set_current_device(target_device, network_name):
                self.continue_to_main_app()
            else:
                # If the device could not be set, display an error message
                print(f"Could not set the selected device {target_device}")
        else:
            print(f"No target device specified {target_device}")
        pass

    @classmethod
    def continue_to_main_app(self):
        """
        Continue to the main app after the device has been selected
        """
        self.nodes_config = []
        self.load_and_add_nodes()
        self.run_commands()

    @classmethod
    def run_commands(self):
        self.order_nodes()
        try:
            nodes_config: dict = yaml.safe_load(
                fm.read_file(Settings.current_device.files.nodes.path)
            )
        except Exception as e:
            LogManager.error(
                f"Could not read nodes configuration file to update it: {e}"
            )



        # Create list of commands
        tmux_commands: List[TmuxPaneCommand] = []

        for node, values in self.nodes_config.items():
            if ("run" in values) and values["run"] is True:
                tmux_commands.append(
                    TmuxPaneCommand(
                        command=values["command"],
                        window=values["window"] if "window" in values else "",
                        delay_ms=int(values["delay_ms"]) if "delay_ms" in values else 0,
                    )
                )

        # Run all the commands
        try:
            # source the workspace before launching the node
            source_cmd = "source " + Settings.current_device.files.workspace_path + "install/setup.{bash,zsh}"
            sh.launch_tmux(tmux_commands, pre_launch_cmd=source_cmd)

            self.get_root().set_tab("Record")
        except Exception as e:
            LogManager.error(f"Unexpected error when trying to run the nodes: {e} \n cmds:" + str(tmux_commands))
            if (self.popup_window is None) or (not self.popup_window.winfo_exists()):
                LogManager.error(f"Could not run the nodes:\n{e}")

    @classmethod
    def load_file(self):
        try:
            self.nodes_config: dict = yaml.safe_load(
                fm.read_file(Settings.current_device.files.nodes.path)
            )
        except Exception as e:
            LogManager.error(f"Could not read nodes configuration file: {e}")
            raise e

        # Set all nodes without "run" field to run by default
        for node_name, values in self.nodes_config.items():
            if "run" not in values:
                values["run"] = True
            elif not isinstance(values["run"], bool):
                values["run"] = False

        self.order_nodes()

        if Settings.current_device.files.source is not None:
            for node_name, values in self.nodes_config.items():
                values["command"] = (
                    f'source {Settings.current_device.files.source.path} && {values["command"]}'
                )

    @classmethod
    def order_nodes(self):
        # Order based on the 'order' field
        self.nodes_config = dict(
            sorted(
                self.nodes_config.items(),
                key=lambda x: int(x[1].get("order", 10**9)),
            )
        )

    @classmethod
    def load_and_add_nodes(self):
        """
        Load the nodes from the configuration file and add them to the frame
        """
        # Load file
        try:
            self.load_file()
        except:
            LogManager.error("Nodes could not be\nloaded with current settings.")

        # Add options
        self.node_entries: List[NodeEntryStruct] = []

        for row, (node_name, values) in enumerate(self.nodes_config.items(), start=2):
            self.node_entries.append(
                NodeEntryStruct(
                    row=row,
                    name=node_name,
                    order=values["order"] if "order" in values else -1,
                    delay_ms=values["delay_ms"] if "delay_ms" in values else 0,
                    window=values["window"] if "window" in values else "",
                    run=values["run"],
                )
            )

        pass


def main():
    parser = argparse.ArgumentParser(
        description="BirdWatchCli - CLI for remote top-level control of UAVs"
    )
    parser.add_argument(
        "-t",
        "--target_device",
        type=str,
        default="",
        help="The target device to connect to (if not found in list of available devices, it will revert to the last used device)",
    )
    parser.add_argument(
        "-n",
        "--network_name",
        type=str,
        default="",
        help="The network name to connect to (if not found in list of available networks, it will revert to the last used network for the used target device)",
    )
    parser.add_argument(
        "-c",
        "--cfg",
        type=str,
        default=None,
        help="The config yaml file for birdwatch ",
    )
    parser.add_argument(
        "-f",
        "--target_device_folder",
        type=str,
        default=None,
        help="Directory containing yaml files for all target devices",
    )
    args = parser.parse_args()
    bw = BirdWatchCli(target_device=args.target_device,
                      network_name=args.network_name,
                      target_device_folder=args.target_device_folder,
                      config_file_path=args.cfg)


if __name__ == "__main__":
    main()
