from typing import List

import customtkinter as ctk
import yaml

import Widgets.ThemedCtkWidgets as tcw
from FileManager import FileManager as fm
from LogManager import LogManager
from PopUpWindows import MessageWindow
from Settings import Settings
from ShellCommands import ShellCommands as sh
from ShellCommands import TmuxPaneCommand


class MissionPreparationTabView(tcw.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.configure(fg_color="transparent")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Add nodes
        self.nodes_frame = NodesFrame(self)
        self.nodes_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="new")

        # Add frame for buttons
        self.buttons_frame = tcw.CTkFrame(self, fg_color="transparent")
        self.buttons_frame.columnconfigure((0, 1), weight=1)
        self.buttons_frame.rowconfigure((0, 1), weight=1)
        self.buttons_frame.grid(row=1, column=0, pady=(0, 10), sticky="esw")

        # Add RViz button
        self.rviz_btn = tcw.CTkButton(
            self.buttons_frame,
            text="Launch RViz",
            width=150,
            command=self.open_rviz,
            tooltip_text="Opens RViz. If a specific configuration file\n"
            + "'default_rviz2.rviz is present in the folder 'config/'"
            + "RViz will be launched with that configuration.\n",
        )
        self.rviz_btn.grid(row=0, column=0, pady=(0, 10), sticky="sw")

        # Add QGroundControl button
        self.qgroundctrl_btn = tcw.CTkButton(
            self.buttons_frame,
            text="Launch QGroundControl",
            width=150,
            command=self.open_qgroundcontrol,
            tooltip_text="Opens QGroundControl. The path to the\nexecutable needs to be set in the field\n"
            + "'qgroundcontrol' of the file 'config/current_config.yaml'",
        )
        self.qgroundctrl_btn.grid(row=1, column=0, pady=(0, 10), sticky="sw")

        # Add run button
        self.run_btn = tcw.CTkButton(
            self.buttons_frame,
            text="Run",
            width=150,
            command=self.run_commands,
            tooltip_text="Opens a Tmux session called 'BirdWatch' in the target device\n"
            + "and runs each selected node in order, in its own pane in the\n"
            + "specified windows. It then opens a terminal in the ground\n"
            + "station and attaches to the Tmux session via SSH",
        )
        self.run_btn.grid(row=0, column=1, pady=(0, 10), sticky="es")

        # Add run button
        self.stop_btn = tcw.CTkButton(
            self.buttons_frame,
            text="Stop",
            width=150,
            command=self.stop_cmd,
            tooltip_text="Closes a Tmux session called 'BirdWatch' in the target device\n"
            + "It then opens a terminal in the ground\n"
            + "station and attaches to the Tmux session via SSH",
        )
        self.stop_btn.grid(row=1, column=1, pady=(0, 10), sticky="es")

        self.soft_stop_btn = tcw.CTkButton(
            self.buttons_frame,
            text="Soft Stop",
            width=150,
            command=self.soft_stop_commands,
            tooltip_text="Stop each node in the Tmux session\n"
                         + "'BirdWatch' by sending 'Ctrl+C' to each pane",
        )
        self.soft_stop_btn.grid(row=2, column=1, pady=(0, 10), sticky="es")

        self.popup_window = None

    def run_commands(self):
        self.nodes_frame.order_nodes()

        # Create list of commands
        tmux_commands: List[TmuxPaneCommand] = []

        for node, values in self.nodes_frame.nodes_config.items():
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
                self.popup_window = MessageWindow(
                    self, f"Could not run the nodes:\n{e}", title="Error"
                )

    def stop_cmd(self):
        self.nodes_frame.order_nodes()
        # Run all the commands
        try:
            # source the workspace before launching the node
            sh.stop_tmux()
        except Exception as e:
            LogManager.error(f"Unexpected error when trying to stop the nodes: {e} \n:")
            if (self.popup_window is None) or (not self.popup_window.winfo_exists()):
                self.popup_window = MessageWindow(
                    self, f"Could not stop the nodes:\n{e}", title="Error"
                )

    def soft_stop_commands(self):
        try:
            pane_list = (
                sh.execute("tmux list-panes -at BirdWatch -F '#S:#I.#P'")
                .strip()
                .split("\n")
            )
        except Exception as e:
            LogManager.error(
                f'Could not find list of panes running in session "BirdWatch": {e}'
            )

        if not pane_list or pane_list == [""]:
            LogManager.warning(f'No panes found for session "BirdWatch"')
            return

        # Send 'Ctrl+C' to each pane
        for pane in pane_list:
            try:
                sh.execute(f"tmux send-keys -t {pane} C-c")
            except Exception as e:
                LogManager.error(f'Could not terminate pane "{pane}": {e}')

    def open_rviz(self):
        try:
            ros_version = sh.execute('echo $ROS_VERSION')
            if ros_version == '1':
                sh.execute_local(f"rviz -d {Settings.default_rviz1_config_file}", timeout=2)
            else:
                sh.execute_local(f"rviz2 -d {Settings.default_rviz2_config_file}", timeout=2)
        except:
            try:
                ros_version = sh.execute('echo $ROS_VERSION')
                if ros_version == '1':
                    sh.execute_local(f"rviz", timeout=2)
                else:
                    sh.execute_local(f"rviz2", timeout=2)
                LogManager.info("rviz2 launched without a configuration file")
            except Exception as e:
                LogManager.error(f'Could not launch "rviz2": {e}')
                if (self.popup_window is None) or (
                    not self.popup_window.winfo_exists()
                ):
                    self.popup_window = MessageWindow(
                        self, "Could not launch rviz2", title="Error"
                    )

    def open_qgroundcontrol(self):
        try:
            sh.execute_local(Settings.qgroundcontrol, timeout=2)
        except Exception as e:
            LogManager.error(f'Could not launch "QGroundControl": {e}')
            if (self.popup_window is None) or (not self.popup_window.winfo_exists()):
                self.popup_window = MessageWindow(
                    self, "Could not launch QGroundControl", title="Error"
                )


class NodesFrame(tcw.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)

        self.columnconfigure((0, 1, 2, 3, 4), weight=1)

        # Add refresh button
        self.refresh_button = tcw.CTkButton(
            self, text="Refresh list", command=self.refresh
        )
        self.refresh_button.grid(
            row=0,
            column=0,
            columnspan=2,
            padx=10,
            pady=(10, 5),
            sticky="nw",
        )

        # Add refresh button
        self.edit_button = tcw.CTkButton(
            self, text="Edit in File", command=self.open_file_to_edit
        )
        self.edit_button.grid(
            row=0,
            column=3,
            columnspan=2,
            padx=10,
            pady=(10, 5),
            sticky="ne",
        )

        # Add column titles
        title_font = ctk.CTkFont(weight="bold")
        self.run_label = tcw.CTkLabel(
            self, text="Run", font=title_font, tooltip_text="Select which nodes to run"
        )
        self.run_label.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="new")

        self.order_label = tcw.CTkLabel(
            self,
            text="Order",
            font=title_font,
            tooltip_text="Order in which the nodes will be run",
        )
        self.order_label.grid(row=1, column=1, padx=5, pady=(5, 10), sticky="new")

        self.delay_label = tcw.CTkLabel(
            self,
            text="Delay (ms)",
            font=title_font,
            tooltip_text="Wait in milliseconds after running the node\nbefore continuing to the next one",
        )
        self.delay_label.grid(row=1, column=2, padx=5, pady=(5, 10), sticky="new")

        self.node_label = tcw.CTkLabel(
            self,
            text="Node",
            font=title_font,
            tooltip_text="Name of the node to run (solely for reference)",
        )
        self.node_label.grid(row=1, column=3, padx=5, pady=(5, 10), sticky="new")

        self.window_label = tcw.CTkLabel(
            self,
            text="Window",
            font=title_font,
            tooltip_text="Tmux window in which to run the node",
        )
        self.window_label.grid(
            row=1, column=4, padx=(5, 10), pady=(5, 10), sticky="new"
        )

        self.load_and_add_nodes()

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

    def order_nodes(self):
        # Order based on the 'order' field
        self.nodes_config = dict(
            sorted(
                self.nodes_config.items(),
                key=lambda x: int(x[1].get("order", 10**9)),
            )
        )

    def load_and_add_nodes(self):
        """
        Load the nodes from the configuration file and add them to the frame
        """
        # Load file
        try:
            self.load_file()
        except:
            self.no_file_label = tcw.CTkLabel(
                self, text="Nodes could not be\nloaded with current settings."
            )
            self.no_file_label.grid(row=2, column=0, pady=(0, 10), columnspan=5)

        # Add options
        self.node_entries: List[NodeEntry] = []

        for row, (node_name, values) in enumerate(self.nodes_config.items(), start=2):
            self.node_entries.append(
                NodeEntry(
                    self,
                    row,
                    node_name,
                    order=values["order"] if "order" in values else -1,
                    delay_ms=values["delay_ms"] if "delay_ms" in values else 0,
                    window=values["window"] if "window" in values else "",
                    run=values["run"],
                )
            )

        # Set the height of the frame so it is not larger than it needs to be
        self.configure(height=self.get_slaves_total_height())

    def refresh(self):
        """
        Refresh the nodes list
        """
        for entry in self.node_entries:
            entry.run_checkbox.destroy()
            entry.order_label.destroy()
            entry.delay_label.destroy()
            entry.node_label.destroy()
            entry.window_label.destroy()

        self.load_and_add_nodes()

    def open_file_to_edit(self):
        sh.open_terminal(command=f"nano {Settings.current_device.files.nodes.path}")

    def update_node_run_in_file(self, node_name: str, run: bool):
        """
        Update the 'run' field of a node in the configuration file

        Parameters:
            node_name (str): Name of the node to update
            run (bool): New value for the 'run' field
        """
        # Read the nodes configuration file
        try:
            nodes_config: dict = yaml.safe_load(
                fm.read_file(Settings.current_device.files.nodes.path)
            )
        except Exception as e:
            LogManager.error(
                f"Could not read nodes configuration file to update it: {e}"
            )

        # Update the 'run' field of the node
        nodes_config[node_name]["run"] = run

        # Write the updated configuration to the file
        try:
            fm.write_file(
                Settings.current_device.files.nodes.path,
                yaml.dump(nodes_config, sort_keys=False),
            )
        except Exception as e:
            LogManager.error(f"Could not write nodes configuration file: {e}")


class NodeEntry:
    def __init__(
        self,
        master: NodesFrame,
        row: int,
        name: str,
        order: int,
        delay_ms: int = 0,
        window=None,
        run: bool = True,
    ):
        self.master = master

        # Add checkbox
        self.run_checkbox = tcw.CTkCheckBox(
            master,
            text="",
            width=0,
            command=self.update_run,
        )
        self.run_checkbox._check_state = run
        self.run_checkbox._draw()
        self.run_checkbox.grid(
            row=row, column=0, padx=(10, 0), pady=(0, 10), sticky="n"
        )

        # Add order
        self.order_label = tcw.CTkLabel(master, text=order if int(order) > 0 else "")
        self.order_label.grid(row=row, column=1, pady=(0, 10), sticky="n")

        # Add delay
        self.delay_label = tcw.CTkLabel(master, text=delay_ms)
        self.delay_label.grid(row=row, column=2, pady=(0, 10), sticky="n")

        # Add node name
        self.node_name = name
        self.node_label = tcw.CTkLabel(master, text=name)
        self.node_label.grid(row=row, column=3, pady=(0, 10), sticky="n")

        # Add window
        self.window_label = tcw.CTkLabel(master, text=window)
        self.window_label.grid(row=row, column=4, pady=(0, 10), sticky="n")

    def update_run(self):
        self.master.nodes_config[self.node_name]["run"] = self.run_checkbox._check_state
        self.master.update_node_run_in_file(
            self.node_name, self.run_checkbox._check_state
        )
