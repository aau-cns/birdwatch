import Widgets.ThemedCtkWidgets as tcw
import customtkinter as ctk
import tkinter
from Widgets.EntryWithLabel import EntryWithLabel
from FileManager import FileManager as fm
import stat
from Settings import Settings
from pathlib import Path
from IconManager import IconManager
from typing import List, Callable
from LogManager import LogManager
import threading
import re


class FileType:
    """
    A class to represent a file type.
    """

    def __init__(self, name: str, extensions: List[str]):
        """
        Initialize the file type.

        Parameters:
            name: The name of the file type.
            extensions: The list of extensions for the file type.
        """
        self.name = name
        self.extensions = extensions

    def matches(self, filename: str) -> bool:
        """
        Check if the file matches the file type.

        Parameters:
            filename: The name of the file.

        Returns:
            bool: Whether the file matches the file type.
        """
        if self.extensions == ["*"]:
            return True
        else:
            return any([filename.endswith(f".{ext}") for ext in self.extensions])

    def __str__(self) -> str:
        """
        Get the string representation of the file type.

        Returns:
            str: The string representation of the file type.
        """
        return (
            self.name + " (" + ", ".join(["*." + ext for ext in self.extensions]) + ")"
        )


class FileDialog(tcw.CTkToplevel):
    def __init__(
        self,
        master,
        select_command: Callable,
        title: str = "File selection",
        initial_dir: str = "~/",
        file_types: List[FileType] = None,
        force_local: bool = False,
        *args,
        **kwargs,
    ):
        """
        Initialize the file dialog.

        Parameters:
            master: The master widget.
            select_command (Callable): The function to call when a file/directory is selected.
            title (str, optional): The title of the dialog.
            initial_dir (str, optional): The initial directory to open.
            file_types (List[FileType], optional): The list of file types to filter by. If the list is empty, all files will be shown, if the list is None, only directories will be shown.
            force_local (bool, optional): Whether to force the dialog to run in local mode
        """
        super().__init__(master, *args, **kwargs)

        self.title(title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
        self.geometry("600x400")

        self.select_command = select_command
        self.run_local = force_local or not Settings.is_ssh_config_set()

        if file_types is not None:
            self.file_types = file_types
            self.file_types.append(FileType("All files", ["*"]))
            self.current_file_type = self.file_types[0]
        else:
            self.current_file_type = None

        # Directory entry
        self.directory_entry_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.directory_entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="new")
        self.directory_entry_frame.columnconfigure(0, weight=1)

        if not fm.exists(initial_dir, force_local=self.run_local):
            initial_dir = "~/"

        self.directory_entry = EntryWithLabel(
            self.directory_entry_frame,
            label="Directory",
            placeholder_text=fm.normalize_path(initial_dir, force_local=self.run_local),
            tooltip="Enter the directory to navigate to and press Enter",
        )
        self.directory_entry.grid(row=0, column=0, padx=10, sticky="new")
        self.directory_entry.entry.bind(
            "<Return>", lambda e: self.move_to(self.directory_entry.get())
        )
        self.directory_entry.entry.bind(
            "<KP_Enter>", lambda e: self.move_to(self.directory_entry.get())
        )

        self.dir_up_btn = tcw.CTkButton(
            self.directory_entry_frame,
            text="",
            image=IconManager.prev_folder.icon,
            width=0,
            command=lambda: self.move_to(str(Path(self.directory_entry.get()).parent)),
            tooltip_text="Go up one directory",
        )
        self.dir_up_btn.grid(row=0, column=1, sticky="ne")

        self.second_row_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.second_row_frame.columnconfigure((0, 1), weight=1)
        self.second_row_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="new")

        # Show hidden elements checkbox
        self.show_hidden_var = tkinter.BooleanVar(value=False)
        self.show_hidden_cb = tcw.CTkCheckBox(
            self.second_row_frame,
            text="Show hidden elements",
            variable=self.show_hidden_var,
            command=lambda: self.move_to(self.directory_entry.get()),
        )
        self.show_hidden_cb.grid(row=0, column=0, padx=(10, 10), sticky="w")

        # Control buttons frame
        self.control_frame = tcw.CTkFrame(self.second_row_frame, fg_color="transparent")
        self.control_frame.grid(row=0, column=1, sticky="e")

        # New folder button
        self.new_folder_btn = tcw.CTkButton(
            self.control_frame,
            text="",
            image=IconManager.new_folder.icon,
            command=self.new_directory_window,
            width=0,
            tooltip_text="Create a new folder",
        )
        self.new_folder_btn.grid(row=0, column=0, sticky="e")

        # Rename button
        self.rename_btn = tcw.CTkButton(
            self.control_frame,
            text="",
            image=IconManager.rename.icon_gray,
            command=self.rename_element_window,
            width=0,
            state="disabled",
            tooltip_text=(
                "Rename the currently selected element",
                "No element selected",
            ),
        )
        self.rename_btn.grid(row=0, column=1, padx=(10, 0), sticky="e")

        # Properties button
        self.properties_btn = tcw.CTkButton(
            self.control_frame,
            text="",
            image=IconManager.properties.icon_gray,
            command=self.properties_window,
            width=0,
            state="disabled",
            tooltip_text=(
                "View the properties of the currently selected element",
                "No element selected",
            ),
        )
        self.properties_btn.grid(row=0, column=2, padx=(10, 0), sticky="e")

        # Delete button
        self.delete_btn = tcw.CTkButton(
            self.control_frame,
            text="",
            image=IconManager.delete.icon_gray,
            command=self.confirm_delete_window,
            width=0,
            state="disabled",
            tooltip_text=(
                "Delete the currently selected element",
                "No element selected",
            ),
        )
        self.delete_btn.grid(row=0, column=3, padx=(10, 0), sticky="e")

        # Create the element list
        self.element_list = ElementList(
            self,
            initial_dir,
            show_hidden=self.show_hidden_var.get(),
            file_type=self.current_file_type,
        )
        self.element_list.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.element_list.configure(height=self.element_list.get_slaves_total_height())

        if file_types is not None:
            self.file_type_frame = tcw.CTkFrame(self, fg_color="transparent")
            self.file_type_frame.columnconfigure(1, weight=1)
            self.file_type_frame.grid(
                row=3, column=0, padx=10, pady=(0, 10), sticky="sew"
            )

            # Create the file type label
            self.file_type_label = tcw.CTkLabel(
                self.file_type_frame, text="Files of type:"
            )
            self.file_type_label.grid(row=0, column=0, padx=10, sticky="w")

            # Create the file type dropdown
            self.file_type_dropdown = tcw.CTkOptionMenu(
                self.file_type_frame,
                values=[str(ft) for ft in self.file_types],
                command=self.on_file_type_selected,
            )
            self.file_type_dropdown.set(str(self.current_file_type))
            self.file_type_dropdown.grid(row=0, column=1, padx=(0, 10), sticky="w")

        self.select_button = tcw.CTkButton(
            master=self if file_types is None else self.file_type_frame,
            text="Select",
            command=self.select,
            tooltip_text=(
                f"Select the currently marked {'file' if file_types is not None else 'directory'}",
                f"Click to mark a {'file' if file_types is not None else 'directory'} before selecting\n(or double click on the {'file' if file_types is not None else 'directory'} to select it).",
            ),
        )
        if file_types is None:
            self.select_button.grid(
                row=3,
                column=0,
                padx=10,
                pady=(0, 10),
                sticky="se",
            )
        else:
            self.select_button.grid(row=0, column=2, sticky="e")

        if file_types is not None:
            self.select_button.configure(state="disabled")

        self.window = None

    def enable_ctrl_btns(self, enable: bool):
        """
        Enable or disable the control buttons.

        Parameters:
            enable: Whether to enable the control buttons.
        """
        if enable:
            self.rename_btn.configure(image=IconManager.rename.icon)
            self.rename_btn.configure(state="normal")
            self.properties_btn.configure(image=IconManager.properties.icon)
            self.properties_btn.configure(state="normal")
            self.delete_btn.configure(image=IconManager.delete.icon)
            self.delete_btn.configure(state="normal")
        else:
            self.rename_btn.configure(image=IconManager.rename.icon_gray)
            self.rename_btn.configure(state="disabled")
            self.properties_btn.configure(image=IconManager.properties.icon_gray)
            self.properties_btn.configure(state="disabled")
            self.delete_btn.configure(image=IconManager.delete.icon_gray)
            self.delete_btn.configure(state="disabled")

    def move_to(self, directory: str):
        """
        Move to the specified directory.

        Parameters:
            directory: The directory to move to.
        """
        new_dir = fm.normalize_path(directory, force_local=self.run_local)
        if not new_dir.endswith("/"):
            new_dir += "/"

        if not fm.exists(new_dir, force_local=self.run_local):
            LogManager.error(f"Directory does not exist: {new_dir}")
            return

        self.directory_entry.set(new_dir)

        self.reload_elements()

    def reload_elements(self):
        """
        Reload the elements in the directory.
        """
        self.element_list.destroy()
        self.element_list = ElementList(
            self,
            self.directory_entry.get(),
            show_hidden=self.show_hidden_var.get(),
            file_type=self.current_file_type,
        )
        self.element_list.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")

        if self.current_file_type is not None:
            self.select_button.configure(state="disabled")
        self.enable_ctrl_btns(False)

    def on_file_type_selected(self, value: str):
        """
        Handle the selection of a file type.

        Parameters:
            value: The value of the selected file type.
        """
        self.current_file_type = next(ft for ft in self.file_types if str(ft) == value)
        self.reload_elements()

    def select(self):
        """
        Select the currently selected element (or the current directory).
        """
        if self.element_list.currently_selected is not None:
            # If an element is selected, select it
            self.select_command(
                self.directory_entry.get()
                + self.element_list.currently_selected.label.cget("text")
            )
        elif self.current_file_type is None:
            # If no element is selected and the dialog is in directory mode, select the current directory
            self.select_command(self.directory_entry.get())

        # Close the dialog
        self.destroy()

    def new_directory_window(self):
        """
        Open the window to create a new directory.
        """
        if self.window is None or not self.window.winfo_exists():
            self.window = ElementNameWindow(
                self,
                title="New directory name",
                select_command=self.create_new_directory,
            )

    def create_new_directory(self, directory_name: str):
        """
        Create a new directory.

        Parameters:
            directory_name: The name of the new directory.
        """
        # Check if the directory already exists
        if fm.exists(
            self.directory_entry.get() + directory_name, force_local=self.run_local
        ):
            LogManager.error(f"Directory already exists: {directory_name}")
            return

        # Create the directory
        fm.mkdir(
            self.directory_entry.get() + directory_name, force_local=self.run_local
        )
        LogManager.info(
            f"Created new directory {self.directory_entry.get() + directory_name} in {'local' if self.run_local else 'remote'} device"
        )

        self.reload_elements()

    def rename_element_window(self):
        """
        Open the window to rename an element.
        """
        if self.element_list.currently_selected is None:
            LogManager.error("No element selected")
            return

        if self.window is None or not self.window.winfo_exists():
            self.window = ElementNameWindow(
                self,
                title="Rename element",
                select_command=self.rename_element,
                element_name=self.element_list.currently_selected.label.cget("text"),
            )

    def rename_element(self, element_name: str):
        """
        Rename an element.

        Parameters:
            element_name: The new name of the element.
        """
        # Check if the name selected is the same as the old one
        if element_name == self.element_list.currently_selected.label.cget("text"):
            LogManager.warning(
                f"New element name is the same as the old one ({element_name}). No changes made."
            )
            return

        # Check if the element already exists
        if fm.exists(
            self.directory_entry.get() + element_name, force_local=self.run_local
        ):
            LogManager.error(f"Element with name {element_name} already exists")
            return

        # Rename the element
        fm.rename(
            self.directory_entry.get()
            + self.element_list.currently_selected.label.cget("text"),
            self.directory_entry.get() + element_name,
            force_local=self.run_local,
        )
        LogManager.info(
            f"Renamed element {self.directory_entry.get() + self.element_list.currently_selected.label.cget('text')} to {element_name} in {'local' if self.run_local else 'remote'} device"
        )

        self.reload_elements()

    def properties_window(self):
        """
        Open the window to view the properties of an element.
        """
        if self.element_list.currently_selected is None:
            LogManager.error("No element selected")
            return

        if self.window is None or not self.window.winfo_exists():
            self.window = ElementPropertiesWindow(
                self,
                element_path=self.directory_entry.get()
                + self.element_list.currently_selected.label.cget("text"),
            )

    def confirm_delete_window(self):
        """
        Open the window to confirm the deletion of an element.
        """
        if self.element_list.currently_selected is None:
            LogManager.error("No element selected")
            return

        if self.window is None or not self.window.winfo_exists():
            self.window = ConfirmDeleteWindow(
                self,
                element_path=self.directory_entry.get()
                + self.element_list.currently_selected.label.cget("text"),
            )


class ElementList(tcw.CTkScrollableFrame):
    def __init__(
        self,
        master: FileDialog,
        directory: str,
        show_hidden: bool = True,
        file_type: FileType = None,
        *args,
        **kwargs,
    ):
        """
        Initialize the element list.

        Parameters:
            master (FileDialog): The master widget.
            directory (str): The directory to show elements for.
            show_hidden (bool, optional): Whether to show hidden files.
            file_type (FileType, optional): The file type to filter by.
        """
        super().__init__(master, *args, **kwargs)

        self.columnconfigure((0, 1, 2), weight=1)

        self.master: FileDialog = master
        self.currently_selected = None
        self.directory = directory
        self.element_type = "directory" if file_type is None else "file"

        if not fm.exists(directory, force_local=self.master.run_local):
            raise FileNotFoundError(f"Directory does not exist: {directory}")

        if not stat.S_ISDIR(
            fm.get_attributes(directory, force_local=self.master.run_local).st_mode
        ):
            raise NotADirectoryError(f"Path is not a directory: {directory}")

        # Get the list of the directories and files
        directories = fm.list_directories(directory, force_local=self.master.run_local)
        directories.sort()
        if not show_hidden:
            directories = [d for d in directories if not d.startswith(".")]

        if file_type is not None:
            files = fm.list_files(directory, force_local=self.master.run_local)
            files.sort()
            if not show_hidden:
                files = [f for f in files if not f.startswith(".")]
            if file_type is not None:
                files = [f for f in files if file_type.matches(f)]

        # Create the elements for the directories and files
        for index, directory in enumerate(directories, start=0):
            entry = ElementEntry(self, directory, element_type="directory")
            entry.grid(
                row=int(index / 3),
                column=0 if index % 3 == 0 else 1 if index % 3 == 1 else 2,
                padx=10,
                pady=(2 if index == 0 else 0, 2),
                sticky="w",
            )

        if file_type is not None:
            for index, file in enumerate(files, start=len(directories)):
                entry = ElementEntry(self, file, element_type="file")
                entry.grid(
                    row=int(index / 3),
                    column=0 if index % 3 == 0 else 1 if index % 3 == 1 else 2,
                    padx=10,
                    pady=(2 if index == 0 else 0, 2),
                    sticky="w",
                )

    def element_selected(self, element: "ElementEntry"):
        """
        Select an element.

        Parameters:
            element: The element to select.
        """
        if self.currently_selected is not None:
            self.currently_selected.deselect()
            if self.element_type == "file":
                self.master.select_button.configure(state="disabled")
            self.master.enable_ctrl_btns(False)

        if self.currently_selected == element:
            self.currently_selected = None
            return
        else:
            element.select()
            self.currently_selected = element
            self.master.enable_ctrl_btns(True)

            if (
                stat.S_ISDIR(
                    fm.get_attributes(
                        self.directory + element.label.cget("text"),
                        force_local=self.master.run_local,
                    ).st_mode
                )
                and self.element_type == "directory"
            ) or (
                stat.S_ISREG(
                    fm.get_attributes(
                        self.directory + element.label.cget("text"),
                        force_local=self.master.run_local,
                    ).st_mode
                )
                and self.element_type == "file"
            ):
                self.master.select_button.configure(state="normal")

    def element_double_clicked(self, element: "ElementEntry"):
        """
        Handle a double click on an element.

        Parameters:
            element: The element that was double clicked.
        """
        if stat.S_ISDIR(
            fm.get_attributes(
                self.directory + element.label.cget("text"),
                force_local=self.master.run_local,
            ).st_mode
        ):
            self.master.move_to(self.directory + element.label.cget("text"))
        else:
            self.master.select_command(self.directory + element.label.cget("text"))
            self.master.destroy()


class ElementEntry(tcw.CTkFrame):
    def __init__(
        self,
        master: ElementList,
        text: str,
        element_type: str,
        *args,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", *args, **kwargs)

        self.master: ElementList = master

        # Create the icon
        self.icon = tcw.CTkLabel(
            self,
            text="",
            width=0,
        )

        # Set the icon based on the element type
        if element_type == "directory":
            if text.startswith("."):
                self.icon.configure(image=IconManager.folder.icon_gray)
            else:
                self.icon.configure(image=IconManager.folder.icon)
        else:
            if text.startswith("."):
                self.icon.configure(image=IconManager.file.icon_gray)
            else:
                self.icon.configure(image=IconManager.file.icon)
        self.icon.grid(row=0, column=0, padx=(0, 10), sticky="w")

        # Create the label
        self.label = tcw.CTkLabel(
            self,
            text=text,
            text_color=(
                ctk.ThemeManager.theme["CTkLabel"]["text_color"]
                if not text.startswith(".")
                else ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"]
            ),
        )
        self.label.grid(row=0, column=1, sticky="w")

        # Bind the events
        self.label.bind("<Button-1>", self.on_single_click)
        self.icon.bind("<Button-1>", self.on_single_click)
        self.label.bind("<Double-Button-1>", self.on_double_click)
        self.icon.bind("<Double-Button-1>", self.on_double_click)

        self.after_id = None

    def on_single_click(self, event):
        """
        Handle a single click on the element.
        """
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.after_id = self.after(200, lambda: self.master.element_selected(self))

    def on_double_click(self, event):
        """
        Handle a double click on the element.
        """
        if self.after_id is not None:
            self.after_cancel(self.after_id)
            self.after_id = None

        self.master.element_double_clicked(self)

    def select(self):
        """
        Select the element.
        """
        self.label.configure(font=ctk.CTkFont(weight="bold"))
        self.label.configure(text_color=Settings.current_device.color_theme.primary)

    def deselect(self):
        """
        Deselect the element.
        """
        self.label.configure(font=ctk.CTkFont(weight="normal"))
        self.label.configure(
            text_color=(
                ctk.ThemeManager.theme["CTkLabel"]["text_color"]
                if not self.label.cget("text").startswith(".")
                else ctk.ThemeManager.theme["CTkButton"]["text_color_disabled"]
            )
        )


class ElementNameWindow(tcw.CTkToplevel):
    def __init__(
        self,
        master: FileDialog,
        title: str,
        select_command: Callable,
        element_name: str = None,
        *args,
        **kwargs,
    ):
        """
        Initialize the element name window.

        Parameters:
            master (FileDialog): The master widget.
            title (str): The title of the window.
            select_command (Callable): The function to call when a element name is selected.
            directory_name (str, optional): The initial element name. If no name is provided, the window will be used to create a new folder.
        """
        super().__init__(master, *args, **kwargs)

        self.title(title)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.geometry("300x100")

        self.select_command = select_command
        self.new_folder = element_name is None

        # Element name entry
        self.element_name_entry = EntryWithLabel(
            self,
            label="Name",
            placeholder_text=element_name if element_name is not None else "",
            tooltip="Enter the name of the element and press Enter",
        )
        self.element_name_entry.grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="new"
        )
        self.element_name_entry.textvar.trace_add(
            "write", lambda *args: self.update_btn()
        )
        self.element_name_entry.entry.focus()
        self.element_name_entry.entry.icursor(tkinter.END)

        # Bind the events
        self.bind("<Return>", lambda e: self.select(self.element_name_entry.get()))
        self.bind("<KP_Enter>", lambda e: self.select(self.element_name_entry.get()))
        self.bind("<Escape>", lambda e: self.destroy())

        # Select button
        self.select_button = tcw.CTkButton(
            self,
            text="Select",
            command=lambda: self.select(self.element_name_entry.get()),
            tooltip_text=(
                "Select the folder name",
                "Name cannot be empty or contain special characters",
            ),
        )
        self.select_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="se")

        self.update_btn()

    def select(self, element_name: str):
        """
        Select the element name.

        Parameters:
            element_name: The name of the element.
        """
        if self.select_button.cget("state") == "normal":
            self.select_command(element_name)
            self.destroy()

    def update_btn(self):
        """
        Update the state of the select button.
        """
        # Check if the directory name is valid
        if (
            self.element_name_entry.get() == ""
            or re.match(r"^[a-zA-Z0-9_][a-zA-Z0-9._-]*$", self.element_name_entry.get())
            is None
        ):
            self.select_button.configure(state="disabled")
        else:
            self.select_button.configure(state="normal")


class ElementPropertiesWindow(tcw.CTkToplevel):
    def __init__(self, master: FileDialog, element_path: str, *args, **kwargs):
        """
        Initialize the element properties window.

        Parameters:
            master (FileDialog): The master widget.
            element_path (str): The path of the element to show properties for.
        """
        super().__init__(master, *args, **kwargs)

        self.title("Properties")
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.master: FileDialog = master
        self.element_path = element_path

        properties = fm.get_attributes(element_path, force_local=master.run_local)
        properties_dict = fm.make_attributes_human_readable(properties)

        # Element name label
        self.element_name_label = tcw.CTkLabel(
            self,
            text=Path(element_path).name,
            font=ctk.CTkFont(weight="bold"),
        )
        self.element_name_label.grid(
            row=0, column=0, padx=20, pady=(20, 10), sticky="n"
        )

        # Element type label
        self.element_type_label = tcw.CTkLabel(
            self,
            text=f"Type: {'directory' if stat.S_ISDIR(properties.st_mode) else 'file'} ({properties_dict['mode']})",
        )
        self.element_type_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="nw")

        # Element size label
        if stat.S_ISDIR(properties.st_mode):
            self.element_size_label = tcw.CTkLabel(
                self,
                text=f"Content size: loading",
            )
            self.dot_count = 0
            self.update_content_loading_label()

            # Start a thread to get the content size (if the directory has many subdirectories and files, this can take a while)
            self.thread = threading.Thread(target=self.update_content_size)
            self.thread.start()
        else:
            self.element_size_label = tcw.CTkLabel(
                self,
                text=f"Size: {properties_dict['size']}",
            )
        self.element_size_label.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="nw")

        # Last modified label
        self.last_modified_label = tcw.CTkLabel(
            self,
            text=f"Last modified: {properties_dict['last_modified']}",
        )
        self.last_modified_label.grid(
            row=3, column=0, padx=20, pady=(0, 5), sticky="nw"
        )

        # Last accessed label
        self.last_accessed_label = tcw.CTkLabel(
            self,
            text=f"Last accessed: {properties_dict['last_accessed']}",
        )
        self.last_accessed_label.grid(
            row=4, column=0, padx=20, pady=(0, 20), sticky="nw"
        )

    def update_content_loading_label(self):
        """
        Update the content size label while the content size is being calculated.
        """
        self.element_size_label.configure(
            text=f"Content size: loading{'.' * self.dot_count}"
        )
        self.dot_count = (self.dot_count + 1) % 4
        self.after_id = self.after(750, self.update_content_loading_label)

    def update_content_size(self):
        """
        Get the content size of the directory.
        """
        try:
            content_size = fm.get_directory_content_size(
                self.element_path,
                force_local=self.master.run_local,
                human_readable=True,
            )
        except Exception as e:
            return

        # Cancel the loading label update
        if hasattr(self, "after_id") and self.after_id is not None:
            self.after_cancel(self.after_id)

        # Update the content size label in a thread-safe way
        self.after(0, lambda: self._set_content_size(content_size))

    def _set_content_size(self, content_size: str):
        """
        Set the content size label.

        Parameters:
            content_size (str): The content size of the directory.
        """
        self.element_size_label.configure(text=f"Content size: {content_size}")

    def destroy(self):
        """
        Destroy the element properties window.
        """
        if fm.cancel_function():
            if hasattr(self, "thread") and self.thread.is_alive():
                self.thread.join(timeout=2)
                if self.thread.is_alive():
                    LogManager.error(
                        "Thread running to get content size did not stop upon request"
                    )
        super().destroy()


class ConfirmDeleteWindow(tcw.CTkToplevel):
    def __init__(self, master: FileDialog, element_path: str, *args, **kwargs):
        """
        Initialize the confirm delete window.

        Parameters:
            master (FileDialog): The master widget.
            element_path (str): The path of the element to delete.
        """
        super().__init__(master, *args, **kwargs)

        self.title("Confirm deletion")
        self.columnconfigure(0, weight=1)
        self.rowconfigure((0, 1, 2), weight=1)

        self.master: FileDialog = master
        self.element_path = element_path

        # Message label
        if stat.S_ISDIR(
            fm.get_attributes(element_path, force_local=self.master.run_local).st_mode
        ):
            self.dir_content = fm.list_contents(
                element_path, force_local=self.master.run_local
            )
            if self.dir_content:
                self.message_label = tcw.CTkLabel(
                    self,
                    text=f"Are you sure you want to delete the\ndirectory '{Path(element_path).name}' and its content?",
                )
            else:
                self.message_label = tcw.CTkLabel(
                    self,
                    text=f"Are you sure you want to delete the\ndirectory '{Path(element_path).name}'?",
                )
        else:
            self.message_label = tcw.CTkLabel(
                self,
                text=f"Are you sure you want to delete the\nfile '{Path(element_path).name}'?",
            )
        self.message_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="n")

        # Delete contents checkbox
        if hasattr(self, "dir_content") and self.dir_content:
            self.delete_contents_var = tkinter.BooleanVar(value=False)
            self.delete_contents_cb = tcw.CTkCheckBox(
                self,
                text="Delete contents",
                variable=self.delete_contents_var,
            )
            self.delete_contents_cb.grid(
                row=1, column=0, padx=20, pady=(0, 10), sticky="nw"
            )

        # Confirm button
        self.confirm_button = tcw.CTkButton(
            self,
            text="Confirm",
            command=self.confirm_delete,
        )
        self.confirm_button.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="se")

        if hasattr(self, "delete_contents_var"):
            self.delete_contents_var.trace_add("write", lambda *args: self.update_btn())
        self.update_btn()

    def confirm_delete(self):
        """
        Confirm the deletion of the element.
        """
        if hasattr(self, "dir_content"):
            try:
                if hasattr(self, "delete_contents_var"):
                    fm.delete_directory(
                        self.element_path,
                        self.delete_contents_var.get(),
                        force_local=self.master.run_local,
                    )
                else:
                    fm.delete_directory(
                        self.element_path, force_local=self.master.run_local
                    )

                LogManager.info(
                    f"Deleted directory {self.element_path} in {'local' if self.master.run_local else 'remote'} device"
                )
            except Exception as e:
                LogManager.error(f"Error deleting directory: {e}")
                return
        else:
            try:
                fm.delete_file(self.element_path, force_local=self.master.run_local)

                LogManager.info(
                    f"Deleted file {self.element_path} in {'local' if self.master.run_local else 'remote'} device"
                )
            except Exception as e:
                LogManager.error(f"Error deleting file: {e}")
                return

        self.master.reload_elements()
        self.destroy()

    def update_btn(self):
        """
        Update the state of the confirm button.
        """
        if not hasattr(self, "delete_contents_var") or self.delete_contents_var.get():
            self.bind("<Return>", lambda e: self.confirm_delete())
            self.bind("<KP_Enter>", lambda e: self.confirm_delete())
            self.confirm_button.configure(state="normal")
        else:
            self.unbind("<Return>")
            self.unbind("<KP_Enter>")
            self.confirm_button.configure(state="disabled")
