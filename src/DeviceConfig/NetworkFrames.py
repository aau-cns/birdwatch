import Widgets.ThemedCtkWidgets as tcw
import tkinter
from DeviceConfig.SSHConfig import NetworkWindow
from DeviceConfig.Network import Network
from ShellCommands import ShellCommands as sh
from LogManager import LogManager
from typing import Callable
from Settings import Settings


class NetworkListFrame(tcw.CTkScrollableFrame):
    def __init__(
        self,
        master,
        set_current_network: Callable = None,
        save: Callable = None,
    ):
        """
        Creates a frame containing all possible networks

        Parameters:
        - master: parent widget
        - set_current_network: function to set the current network
        - save: function to save the changes
        """
        super().__init__(master, fg_color="transparent")

        self.columnconfigure(0, weight=1)

        self.networks_frames = []

        self.selected_network_index = tkinter.IntVar(
            value=Settings.current_device.ssh_config.selected_network
        )

        # Add all available networks for the currently selected target device
        for index, network in enumerate(
            Settings.current_device.ssh_config.networks, start=0
        ):
            network_frame = NetworkFrame(
                self,
                network=network,
                radio_var=self.selected_network_index,
                index=index,
                set_current_network=set_current_network,
                save=save,
            )
            network_frame.grid(row=index, column=0, pady=2, sticky="new")
            self.networks_frames.append(network_frame)

        # Set the height of the frame so it is not larger than in needs to be
        self.configure(height=self.get_slaves_total_height())

    def add_network(self, network: Network):
        """
        Add a new network to the list

        Parameters:
        - network: network to add
        """
        index = self.networks_frames.__len__()

        # Create Network Frame
        network_frame = NetworkFrame(
            self,
            network=network,
            radio_var=self.selected_network_index,
            index=index,
            set_current_network=None,
            save=None,
        )
        network_frame.grid(row=index, column=0, pady=2, sticky="new")
        self.networks_frames.append(network_frame)

        # Select the new network
        network_frame.radio_btn.select()
        Settings.current_device.ssh_config.selected_network = index

        # Adjust the height of the frame
        self.configure(height=self.get_slaves_total_height())

        # Scroll to the bottom
        self._parent_canvas.yview_moveto(1)


class NetworkFrame(tcw.CTkFrame):
    def __init__(
        self,
        master,
        network: Network,
        radio_var: tkinter.IntVar,
        index: int,
        set_current_network: Callable = None,
        save: Callable = None,
    ):
        """
        Add entry of a single network

        Parameters:
        - master: parent widget
        - network: network to display
        - radio_var: variable to keep track of the selected network
        - index: index of the network in the list
        - set_current_network: function to set the current network
        - save: function to save the changes
        """
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.set_current_network = set_current_network
        self.save = save

        # Add Radio Button and text
        self.network = network
        self.radio_btn = tcw.CTkRadioButton(
            self,
            text=f"{network.name}\n{network.ip}",
            variable=radio_var,
            value=index,
            command=self.select_network,
        )
        self.radio_btn.grid(row=0, column=0, padx=(0, 5), sticky="w")

        # Add "Edit" button
        self.edit_btn = tcw.CTkButton(
            self,
            text="Edit",
            width=0,
            command=self.edit_network,
        )
        self.edit_btn.grid(row=0, column=1, sticky="e")
        self.network_window = None

        # Add "Delete" button
        self.delete_btn = tcw.CTkButton(
            self,
            text="Delete",
            width=0,
            command=self.delete_network,
        )
        self.delete_btn.grid(row=0, column=2, padx=(5, 0), sticky="ew")

    def select_network(self):
        """
        Select the network and save the changes
        """
        Settings.current_device.ssh_config.selected_network = self.radio_btn.cget(
            "value"
        )

        sh.close_ssh()

        if self.set_current_network is not None:
            self.set_current_network(
                Settings.current_device.ssh_config.selected_network
            )

        if self.save is not None:
            self.save()

    def edit_network(self):
        """
        Open a window to edit the network
        """
        if self.network_window is None or not self.network_window.winfo_exists():
            self.network_window = NetworkWindow(
                self,
                Settings.current_device.ssh_config,
                name=self.network.name,
                ip=self.network.ip,
                confirm_command=self.network_edited,
            )

    def network_edited(self):
        """
        Save the changes made to the network
        """
        if self.save is not None:
            self.save()

        # Update the radio button text
        self.radio_btn.configure(text=f"{self.network.name}\n{self.network.ip}")

        # Select the network
        self.radio_btn.select()
        Settings.current_device.ssh_config.selected_network = self.radio_btn.cget(
            "value"
        )

    def delete_network(self):
        """
        Delete the network
        """
        if Settings.current_device.ssh_config.networks.__len__() == 1:
            LogManager.error("Cannot delete last available network")
            return

        # Find selected network
        network = next(
            (
                network
                for network in Settings.current_device.ssh_config.networks
                if network.name == self.network.name
            ),
            None,
        )
        if network is None:
            LogManager.error("Unexpected error: network selected to delete not found")
            return

        # Remove network from list of available networks
        try:
            Settings.current_device.ssh_config.networks.remove(network)
        except ValueError as e:
            LogManager.error(e)
            return

        # If the network deleted was the current one, select the first available
        if (
            self.radio_btn.cget("value")
            == Settings.current_device.ssh_config.selected_network
        ):
            Settings.current_device.ssh_config.selected_network = 0

        if self.save is not None:
            self.save()
        self.master.refresh()
