from DeviceConfig.Network import Network
import customtkinter as ctk
import Widgets.ThemedCtkWidgets as tcw
import tkinter
from LogManager import LogManager
from typing import Union, Callable, Any, List


class SSHConfig:
    def __init__(self, username: str):
        """
        Configuration necessary to stablish an SSH connection with a remote device.

        Args:
            username (string): username to login to on the remote device.

        Attributes:
            networks (list): A list of possible IP addresses for the device in different networks.

        Example:
            ssh_config = SSHConfig("user")
            ssh_config.add_network("home_network", "192.168.0.115")
        """
        self.username = username
        self.networks: List[Network] = []
        self.selected_network = None

    def add_network(self, name: str, ip: str):
        """
        Add a possible network through which to stablish an SSH connection to a device

        Args:
            name (string): name of the network
            ip (string): ip of the device in the network
        """
        try:
            self.networks.append(Network(name, ip))

            # If it is the first added network, select it
            if self.networks.__len__() == 1:
                self.selected_network = 0
        except ValueError as e:
            raise e

    def edit_network(self, name: str, new_name: str = None, new_ip: str = None):
        """
        Edit a network through which to stablish an SSH connection to a device

        Args:
            name (string): original name of the network
            new_name (string, optional): new name of the network
            new_ip (string): new ip of the device in the network
        """
        index = next(
            (
                index
                for index, network in enumerate(self.networks)
                if network.name == name
            ),
            None,
        )
        if index is None:
            raise ValueError(f'Network with old name "{name}" not found')

        try:
            self.networks[index].update(new_name, new_ip)
        except Exception as e:
            raise e

    def select_network(self, network_index: int):
        """
        Select a network on which to stablish an SSH connection to a device

        Args:
            network_index (int): index (starting from 0) of the network to connect to
        """
        if self.networks.__len__() > network_index:
            self.selected_network = network_index
        else:
            raise ValueError(
                f"No network available with the given index {network_index} (only {self.networks.__len__()} network/s available)"
            )

    def get_network_index(self, name: str) -> int:
        """
        Get the index of the network with the given name

        Args:
            name (string): name of the network

        Returns:
            int: index of the network
        """
        return next(
            (
                index
                for index, network in enumerate(self.networks)
                if network.name == name
            ),
            None,
        )

    def to_dictionary(self) -> dict:
        ssh_dict = {
            "username": self.username,
            "selected_network": self.selected_network,
            "networks": [],
        }

        ssh_dict["networks"] = []
        for i, network in enumerate(self.networks, start=0):
            ssh_dict["networks"].append(network.to_dictionary())

        return ssh_dict


class NetworkWindow(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        ssh_config: SSHConfig,
        name: str = None,
        ip: str = None,
        confirm_command: Union[Callable[[], Any], None] = None,
    ):
        """
        Creates a window to add a network (or edit it if name and/ip
        are given as parameter)

        Parameters:
            master: The parent widget.
            name (string, optional): original name of the network.
            ip (string, optional): original IP address of the network.
            confirm_command (Callable, optional): function when the confirm button is clicked.

        Example:
            window = None

            def add_network():
                if window is None or not window.winfo_exists():
                    window = NetworkWindow(
                        master,
                        ssh_config
                    )
        """
        super().__init__(master)
        self.wm_group(".")

        if ip is not None:
            self.window_title = "Edit network"
            if name is not None:
                self.original_name = name

        else:
            self.window_title = "Add network"

        self.ssh_config = ssh_config
        self.confirm_command = confirm_command

        # Configure window
        self.title(self.window_title)

        # Add widgets
        self.add_name_line(name)
        self.add_ip_line(ip)
        self.add_buttons()

        # Block parent window, forcing user to confirm/cancel first
        self.update_idletasks()
        self.grab_set()

        self.bind("<Return>", lambda event: self.confirm())
        self.bind("<KP_Enter>", lambda event: self.confirm())
        self.bind("<Escape>", lambda event: self.cancel())

    def add_name_line(self, name: str):
        self.name_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.name_frame.grid(
            row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="new"
        )

        # Add label
        self.name_label = tcw.CTkLabel(self.name_frame, text="Name:")
        self.name_label.grid(row=0, column=0, sticky="nw")

        # Add entry
        self.name_variable = tkinter.StringVar(value=name)
        self.name_entry = tcw.CTkEntry(self.name_frame, textvariable=self.name_variable)
        self.name_entry.tooltip = tcw.ToolTip(self.name_entry, "")
        self.name_entry.grid(row=0, column=1, padx=(10, 0), sticky="ne")

        # Add trace to update confirm button state when the name is changed
        self.name_variable.trace_add("write", self.update_confirm_btn_state)

    def add_ip_line(self, ip: str):
        self.ip_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.ip_frame.grid(
            row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="new"
        )

        # Add label
        self.ip_label = tcw.CTkLabel(self.ip_frame, text="IP:")
        self.ip_label.grid(row=0, column=0, sticky="nw")

        # Add entry
        self.ip_variable = tkinter.StringVar(value=ip)
        self.ip_entry = tcw.CTkEntry(self.ip_frame, textvariable=self.ip_variable)
        self.ip_entry.tooltip = tcw.ToolTip(self.ip_entry, "")
        self.ip_entry.grid(row=0, column=1, padx=(10, 0), sticky="ne")

        # Add trace to update confirm button state when the IP is changed
        self.ip_variable.trace_add("write", self.update_confirm_btn_state)

    def add_buttons(self):
        # Add "Confirm" button
        self.confirm_btn = tcw.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_btn.tooltip = tcw.ToolTip(self.confirm_btn, "")
        self.confirm_btn.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nw")

        # Add "Cancel" button
        self.cancel_btn = tcw.CTkButton(
            self, text="Cancel", command=self.cancel, font=ctk.CTkFont(weight="bold")
        )
        self.cancel_btn.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="ne")

        self.update_confirm_btn_state()

    def update_confirm_btn_state(self, *args):
        """
        Enable/Disable the confirm button based on the validity of the name and IP
        """
        # Check if the name is valid
        if self.name_variable.get() == "":
            name_valid = False
            self.name_entry.tooltip.text = "Name cannot be empty"
        else:
            name_valid = True
            self.name_entry.tooltip.text = ""

        # Check if the IP is valid
        if Network.is_valid_ip(self.ip_variable.get()):
            ip_valid = True
            self.ip_entry.tooltip.text = ""
        else:
            ip_valid = False
            self.ip_entry.tooltip.text = "Invalid IP address"

        # Enable/Disable the confirm button
        if name_valid and ip_valid:
            self.confirm_btn.configure(state="normal")
            self.confirm_btn.tooltip.text = ""
        else:
            self.confirm_btn.configure(state="disabled")
            self.confirm_btn.tooltip.text = "Name and IP must be valid"

    def confirm(self):
        """
        Add or edit the network and close the window
        """
        try:
            if self.window_title == "Add network":
                self.ssh_config.add_network(
                    self.name_variable.get(), self.ip_variable.get()
                )
            else:
                self.ssh_config.edit_network(
                    self.original_name,
                    new_name=self.name_variable.get(),
                    new_ip=self.ip_variable.get(),
                )

        except ValueError as e:
            LogManager.error(e)
            return

        if self.confirm_command is not None:
            self.confirm_command()
        self.destroy()

    def cancel(self):
        self.destroy()
