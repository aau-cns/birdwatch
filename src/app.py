#!/usr/bin/env python

import threading
from PIL import Image, ImageTk
import customtkinter as ctk
from functools import wraps

from TabViews import (
    ParametersTabView,
    MissionPreparationTabView,
    RecordTopicsTabView,
)

import Widgets.ThemedCtkWidgets as tcw
from LogManager import LogManager
import argparse

from from_root import from_root
from IconManager import IconManager
from SelectDevice import DeviceSelectionFrame
import signal
from Widgets.CollapsibleLogBox import CollapsibleLoggingTextbox
from Settings import Settings

def thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
        return thread

    return wrapper


class App(ctk.CTk):

    info_lock = threading.Lock()

    def __init__(self, target_device: str = None, network_name: str = None,
                 config_file_path: str = None, target_device_folder: str = None):

        super().__init__(className="BirdWatch")

        ctk.set_appearance_mode("dark")

        # Configure window
        self.title("BirdWatch")
        self.geometry("500x1000")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=3, uniform="row")
        self.rowconfigure(1, weight=1, uniform="row")

        # Set it so that all windows are grouped under the root window
        self.wm_group(".")

        # Set default app icon
        self.set_icon(None)

        # Initialize icons
        IconManager.initialize()

        # Initialize logger
        LogManager.init()

        # Load settings from config
        Settings.set_paths(config_file_path, target_device_folder)

        # Load settings from config
        Settings.load_config()

        # Set the root app
        Settings.set_root_app(self)

        # Add logging textbox
        self.add_logging_textbox()

        # Load possible target devices configured
        Settings.load_devices()

        if target_device is None:
            # Create frame for selecting device
            self.select_device_frame = DeviceSelectionFrame(
                self, self.continue_to_main_app
            )
            self.select_device_frame.grid(
                row=0, column=0, padx=20, pady=20, sticky="nesw"
            )
        else:
            # Set the selected device
            if Settings.set_current_device(target_device, network_name):
                self.continue_to_main_app()
            else:
                # If the device could not be set, display an error message
                LogManager.error(f"Could not set the selected device {target_device}")
                self.wrong_device_label = tcw.CTkLabel(
                    self,
                    text="Could not find configuration for the selected device",
                )
                self.wrong_device_label.grid(row=0, column=0, padx=20, pady=(20, 10))

    def continue_to_main_app(self):
        """
        Continue to the main app after the device has been selected
        """
        # Create main app frame
        self.root_frame = RootFrame(self)
        self.root_frame.grid(row=0, column=0, sticky="nesw")

    def set_icon(self, icon_path: str):
        """
        Set the app icon

        Parameters:
            icon_path (str): Path to the icon file. If None, the default icon will be set
        """
        try:
            icon = Image.open(
                icon_path
                if icon_path is not None
                else from_root("resources/logos/White.png")
            )
            photo = ImageTk.PhotoImage(icon)
            self.iconphoto(True, photo)
        except Exception as e:
            if icon_path is None:
                LogManager.error(f"Could not set default icon: {e}")
            else:
                LogManager.error(f"Could not set icon {icon_path}: {e}")
                self.set_icon(None)

    def add_logging_textbox(self):
        """
        Add a logging textbox to the app
        """
        self.logging_textbox = CollapsibleLoggingTextbox(self)
        self.logging_textbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nesw")

        # Set the textbox for the LogManager
        LogManager.set_textbox(self.logging_textbox.logging_textbox)

    def ctrl_c_handler(self, signum, frame):
        """
        Handler for Ctrl-C signal
        """
        print("")
        LogManager.info("Ctrl-C pressed")
        self.exit()

    def ctrl_z_handler(self, signum, frame):
        """
        Handler for Ctrl-Z signal
        """
        print("")
        LogManager.info("Ctrl-Z pressed")
        self.exit()

    def window_close_handler(self):
        """
        Handler for window close event
        """
        LogManager.info("Window closed")
        self.exit()

    def exit(self):
        """
        Exit the main app
        """
        self.quit()


class RootFrame(tcw.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.tabs = tcw.CTkTabview(self, fg_color="transparent")
        self.tabs.columnconfigure(0, weight=1)
        self.tabs.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nesw")

        # Add Parameters TabView
        self.tabs.add("Parameters")
        self.tabs.tab("Parameters").columnconfigure(0, weight=1)
        self.tabs.tab("Parameters").rowconfigure(0, weight=1)
        self.parameters_tabview = ParametersTabView(self.tabs.tab("Parameters"))
        self.parameters_tabview.grid(row=0, column=0, sticky="nesw")

        # Add Mission Preparation TabView
        self.tabs.add("Mission Preparation")
        self.tabs.tab("Mission Preparation").columnconfigure(0, weight=1)
        self.tabs.tab("Mission Preparation").rowconfigure(0, weight=1)
        self.missionprep_tabview = MissionPreparationTabView(
            self.tabs.tab("Mission Preparation")
        )
        self.missionprep_tabview.grid(row=0, column=0, sticky="nesw")

        # Add Record TabView
        self.tabs.add("Record")
        self.tabs.tab("Record").columnconfigure(0, weight=1)
        self.tabs.tab("Record").rowconfigure(0, weight=1)
        self.record_tabview = RecordTopicsTabView(self.tabs.tab("Record"))
        self.record_tabview.grid(row=0, column=0, sticky="nesw")

        self.set_tab()

    def set_tab(self, tab: str = "Mission Preparation"):
        try:
            self.tabs.set(tab)
        except ValueError as e:
            LogManager.error(f"Invalid tab {tab}: {e}")


def main():

    parser = argparse.ArgumentParser(
        description="BirdWatch - Graphical User Interface for remote monitoring and top-level control of UAVs"
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

    app = App(
        target_device=args.target_device if args.target_device != "" else None,
        network_name=args.network_name if args.network_name != "" else None,
        config_file_path=args.cfg,
        target_device_folder=args.target_device_folder,
    )

    # Set signal handlers
    signal.signal(signal.SIGINT, app.ctrl_c_handler)
    signal.signal(signal.SIGTSTP, app.ctrl_z_handler)
    app.protocol("WM_DELETE_WINDOW", app.window_close_handler)

    app.mainloop()
    app.destroy()


if __name__ == "__main__":
    main()
