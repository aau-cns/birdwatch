import customtkinter as ctk
from typing import Tuple
from from_root import from_root
from PIL import Image


class Icon:
    def __init__(self, icon_name: str, size: Tuple[int, int]):
        """
        Initialize the icon.

        Parameters:
            icon_name: The name of the icon.
            size: The size of the icon.
        """
        # Path to the icons
        self.root_path = from_root("resources/icons/")

        # Set the name and size of the icon
        self.name = icon_name
        self.size = size

        # Load the icon
        self.icon = ctk.CTkImage(
            dark_image=Image.open(f"{self.root_path}/{icon_name}.png"), size=size
        )

        # Load the gray icon (used for disabled state)
        self.icon_gray = ctk.CTkImage(
            dark_image=Image.open(f"{self.root_path}/{icon_name}_gray.png"), size=size
        )


class IconManager:
    """
    A class to manage the icons used in the application.
    """

    arrow_up: Icon
    arrow_down: Icon
    edit: Icon
    delete: Icon

    @classmethod
    def initialize(cls):
        """
        Initialize the icons.
        """
        # From https://uxwing.com/chevron-direction-top-icon/
        cls.arrow_up = Icon("arrow_up", (16, 9))

        # From https://uxwing.com/chevron-direction-bottom-icon/
        cls.arrow_down = Icon("arrow_down", (16, 9))

        # From https://uxwing.com/edit-pen-icon/
        cls.edit = Icon("edit", (14, 15))

        # From https://uxwing.com/expand-all-icon/
        cls.add = Icon("add", (15, 14))

        # From https://uxwing.com/eraser-icon/
        cls.delete = Icon("delete", (14, 16))

        # From https://uxwing.com/text-file-black-icon/ (and modified)
        cls.file = Icon("file", (13, 16))

        # From https://uxwing.com/folder-line-icon/ (and modified)
        cls.folder = Icon("folder", (16, 13))
        cls.prev_folder = Icon("prev_folder", (16, 13))
        cls.new_folder = Icon("new_folder", (16, 13))

        # Custom made
        cls.rename = Icon("rename", (16, 14))

        # From https://uxwing.com/sliders-icon/
        cls.properties = Icon("properties", (16, 16))
