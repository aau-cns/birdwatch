import tkinter
from typing import Callable, List

import Widgets.ThemedCtkWidgets as tcw
from DeviceConfig.SSHConfigFrame import SSHConfigFrame
from LogManager import LogManager
from PopUpWindows import MessageWindow
from Settings import Settings
from ShellCommands import ShellCommands as sh


class SelectDeviceFrame(tcw.CTkScrollableFrame):
    def __init__(
        self, master: "DeviceSelectionFrame", device_selected_command: Callable
    ):
        super().__init__(master)

        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1), weight=1)

        self.tooltip = (
            "To configure a new device, add a new YAML\n"
            + "file to the 'config/target_devices' folder.\n"
            + "You can use 'Template.yaml' as a reference."
        )

        # Add section title
        self.label = tcw.CTkLabel(
            self, text="Select the device to connect to:", tooltip_text=self.tooltip
        )
        self.label.grid(row=0, column=0, padx=10, pady=5, sticky="new")

        # Add frame for device selection
        self.devices_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.devices_frame.grid(row=1, column=0, padx=10, sticky="nesw")

        # Add radio buttons for each device
        self.selected_device_var = tkinter.IntVar(value=0)
        self.device_radiobuttons: List[tcw.CTkRadioButton] = []

        for index, device in enumerate(Settings.target_devices, start=1):
            radiobutton = tcw.CTkRadioButton(
                self.devices_frame,
                text=device.name,
                variable=self.selected_device_var,
                value=index,
                command=device_selected_command,
                fg_color=device.color_theme.primary,
                hover_color=device.color_theme.dark_primary,
                tooltip_text=self.tooltip,
            )
            radiobutton.grid(
                row=index,
                column=0,
                pady=(
                    0 if index == 1 else 5,
                    5,
                ),
                sticky="new",
            )
            self.devices_frame.rowconfigure(index, weight=1)
            self.device_radiobuttons.append(radiobutton)

        # Set the height of the frame so it is not larger than in needs to be
        self.configure(height=self.get_slaves_total_height())


class DeviceSelectionFrame(tcw.CTkFrame):
    def __init__(self, master, confirm_selection: Callable):
        super().__init__(master, fg_color="transparent")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.select_device_frame = SelectDeviceFrame(self, self.device_selected)
        self.select_device_frame.grid(row=0, column=0, pady=(0, 10), sticky="new")

        self.confirm_selection = confirm_selection

        self.confirm_button = None
        self.ssh_frame = None
        self.confirmation_window = None

    def device_selected(self):
        """
        Set the current device to the selected one and add the SSH configuration
        """
        # Set the current device to the selected one
        try:
            Settings.set_current_device(
                Settings.target_devices[
                    self.select_device_frame.selected_device_var.get() - 1
                ].name,
            )
        except Exception as e:
            LogManager.error(
                f"Could not set the selected device: {e}"
            )
            #LogManager.error(f"Could not set the selected device")
            return

        # Destroy the SSH frame if it exists
        if self.ssh_frame is not None:
            self.ssh_frame.destroy()
            self.ssh_frame = None

        # Add the SSH frame if the device has SSH configuration
        if Settings.current_device.ssh_config is not None:

            self.ssh_frame = SSHConfigFrame(
                self,
            )
            self.ssh_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
            self.rowconfigure(1, weight=1)

        # Destroy the confirm button if it exists
        if self.confirm_button is not None:
            self.confirm_button.destroy()

        # Add the confirm button
        self.confirm_button = tcw.CTkButton(
            self,
            text="Confirm",
            command=self.confirm,
        )
        self.confirm_button.grid(row=2, column=0, sticky="es")
        self.rowconfigure(2, weight=1)

    def confirm(self):
        """
        Confirm the selection and close the window
        """
        if Settings.current_device.ssh_config is not None:
            # Set the current network to the selected one
            Settings.set_current_network(
                network_index=Settings.current_device.ssh_config.selected_network
            )

            # Check if SSH connection works
            try:
                sh.establish_ssh()
            except Exception as e:
                if (
                    self.confirmation_window is None
                    or not self.confirmation_window.winfo_exists()
                ):
                    self.confirmation_window = MessageWindow(
                        self,
                        title="Connection error",
                        message=f"Could not connect to {Settings.current_device.name}\nvia {Settings.current_device.ssh_config.networks[Settings.current_device.ssh_config.selected_network].name} ({Settings.current_device.ssh_config.networks[Settings.current_device.ssh_config.selected_network].ip})",
                    )
                return

        Settings.save_device(Settings.current_device)

        self.confirm_selection()
