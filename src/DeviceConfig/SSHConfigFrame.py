import Widgets.ThemedCtkWidgets as tcw
import customtkinter as ctk
import tkinter
from DeviceConfig.NetworkFrames import NetworkListFrame
from DeviceConfig.SSHConfig import NetworkWindow
from typing import Callable
from Settings import Settings


class SSHConfigFrame(tcw.CTkFrame):
    def __init__(
        self,
        master,
        save_command: Callable = None,
        set_current_network: Callable = None,
    ):
        """
        Creates a frame containing the SSH configuration for the current
        target device, including username and possible networks

        Parameters:
        - master: parent widget
        - save_command: function to save the changes
        - set_current_network: function to set the current network
        """
        super().__init__(master)

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3), weight=1)

        self.save_command = save_command

        # Add section title
        self.title = tcw.CTkLabel(
            self, text="SSH Configuration", font=ctk.CTkFont(weight="bold")
        )
        self.title.grid(row=0, column=0, padx=10, pady=(5, 0), sticky="n")

        # Add label "Username: "
        self.add_username(1)

        # Add possible networks
        self.network_list_frame = NetworkListFrame(
            self, set_current_network, save_command
        )
        self.network_list_frame.grid(row=2, column=0, padx=10, sticky="new")
        self.network_window = None

        # Add "Add network" button
        self.add_network_btn = tcw.CTkButton(
            self,
            text="Add network",
            width=0,
            command=self.add_new_network,
        )
        self.add_network_btn.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="sw")

        # Set the height of the frame so it is not larger than in needs to be
        self.configure(height=self.get_slaves_total_height())

    def add_username(self, row: int):
        self.username_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.username_frame.columnconfigure(1, weight=1)
        self.username_frame.rowconfigure(0, weight=1)

        self.username_label = tcw.CTkLabel(
            self.username_frame,
            text="Username:",
        )
        self.username_label.grid(row=0, column=0, padx=(0, 10), sticky="nsw")

        self.username_textvar = tkinter.StringVar(
            value=Settings.current_device.ssh_config.username
        )
        self.username_textvar.trace_add("write", self.on_username_changed)

        self.username_entry = tcw.CTkEntry(
            self.username_frame,
            textvariable=self.username_textvar,
        )
        self.username_entry.grid(row=0, column=1, sticky="news")

        self.username_frame.grid(row=row, column=0, padx=10, pady=5, sticky="new")

    def on_username_changed(self, *args):
        """
        Callback function for when the username is changed
        """
        Settings.current_device.ssh_config.username = self.username_textvar.get()
        if self.save_command is not None:
            self.save_command()

    def add_new_network(self):
        """
        Open a window to add a new network
        """
        if self.network_window is None or not self.network_window.winfo_exists():
            self.network_window = NetworkWindow(
                self,
                Settings.current_device.ssh_config,
                confirm_command=self.network_added,
            )

    def network_added(self):
        """
        Callback function for when a new network is added
        """
        if self.save_command is not None:
            self.save_command()
        self.network_list_frame.add_network(
            Settings.current_device.ssh_config.networks[-1]
        )

        # Adjust the height of the frame
        self.configure(height=self.get_slaves_total_height())
