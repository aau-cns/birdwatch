import subprocess
from collections import OrderedDict
from time import sleep
from typing import List

import paramiko

from LogManager import LogManager
from Settings import Settings


class CommandError(Exception):
    pass


class TmuxPaneCommand:
    def __init__(self, command: str, window: str, delay_ms: int = 0):
        self.command = command
        self.window = window
        self.delay_ms = delay_ms


class ShellCommands:
    ssh: paramiko.SSHClient = None

    @classmethod
    def establish_ssh(cls):
        """
        Established an SSH connection with the configuration in Settings
        """
        if cls.ssh is None:
            # Create client
            cls.ssh = paramiko.SSHClient()
            cls.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Establish connection to current remote device
        try:
            LogManager.info(
                f"Connecting to {Settings.current_device.name} on {Settings.current_device.ssh_config.username}@{Settings.current_device.ssh_config.networks[Settings.current_device.ssh_config.selected_network].ip}..."
            )
            cls.ssh.connect(
                Settings.current_device.ssh_config.networks[
                    Settings.current_device.ssh_config.selected_network
                ].ip,
                username=Settings.current_device.ssh_config.username,
                timeout=5,
            )
            LogManager.info("Connection successful")
        except Exception as e:
            LogManager.error(f"Failed to establish SSH connection: {e}")
            raise

    @classmethod
    def execute(cls, command: str):
        """
        Executes a linux command either locally or remote (if a valid
        SSH configuration is set in Settings)

        Parameters:
            command (string): Command to execute
        """
        try:
            if Settings.is_ssh_config_set():
                try:
                    # Execute command via SSH
                    stdin, stdout, stderr = cls.ssh.exec_command(command)
                except:
                    # Close any possible previous SSH session
                    cls.close_ssh()
                    # Establish SSH connection
                    try:
                        cls.establish_ssh()
                    except Exception as e:
                        raise e

                    # Try to execute the command again
                    stdin, stdout, stderr = cls.ssh.exec_command(command)

                if not stderr.read():
                    return stdout.read().decode("utf-8")
                else:
                    raise CommandError(stderr.read())
            else:
                try:
                    # Run the command and capture the output
                    return cls.execute_local(command)
                except CommandError as e:
                    # If the command fails, handle the error
                    raise e
        except (CommandError, paramiko.SSHException) as e:
            raise e

    @classmethod
    def execute_local(cls, command: str, timeout: int = 0):
        """
        Executes a Linux command locally.

        Parameters:
            command (string): Command to execute
            timeout (optional, int): Time during which to expect an error in commands,
                                    that keep running. If no error happens after this
                                    time, the function returns

        Returns:
            generator: A generator that yields lines of output from the command.
                       If the command fails immediately, raises CommandError.

        Example:
            try:
                output_gen = ShellCommands.execute_local("your_command_here")
                for output in output_gen():
                    print(output)
            except CommandError as e:
                print(f"Command failed with error: {e}")
        """
        try:
            # Start the command as a subprocess
            process = subprocess.Popen(
                "cd && " + command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if timeout > 0:
                # Capture the first output to check for immediate failure
                stdout, stderr = process.communicate(timeout=timeout)

                if process.returncode != 0:
                    # If the command fails initially, raise an error
                    raise CommandError(stderr.decode("utf-8"))
            else:
                # Wait indefinitely for the command to complete
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    raise CommandError(stderr.decode("utf-8"))
                return stdout.decode("utf-8")

        except subprocess.TimeoutExpired:
            # If it hits the timeout, assume the command is running correctly
            pass
        except subprocess.CalledProcessError as e:
            raise CommandError(e.output.decode("utf-8"))

        def output_generator():
            while True:
                output = process.stdout.readline()
                if output:
                    yield output.decode("utf-8")
                elif process.poll() is not None:
                    break

        return output_generator

    @classmethod
    def open_terminal(cls, command: str = None, force_local: bool = False):
        """
        Opens a terminal

        Parameters:
            command (string, optional): Command to execute on the new terminal upon opening
        """
        if command is None:
            cls.execute_local("gnome-terminal")
        elif Settings.is_ssh_config_set() and not force_local:
            cls.execute_local(
                f"gnome-terminal -- bash -c \"ssh -t {Settings.current_device.ssh_config.username}@{Settings.current_device.ssh_config.networks[Settings.current_device.ssh_config.selected_network].ip} '{command}'; exec bash\""
            )
        else:
            cls.execute_local(f'gnome-terminal -- bash -c "{command}; exec bash"')

    @classmethod
    def close_ssh(cls):
        """
        Closes a previously stablished SSH connections
        """
        if cls.ssh is not None:
            cls.ssh.close()
            cls.ssh = None

    @classmethod
    def launch_tmux_from_dict(
        cls, commands: dict, session_name: str = "BirdWatch", auto_attach: bool = True
    ):
        """
        Creates a tmux session and opens windows and panes running commands on them as specified by "commands"; and then opens a terminal and attaches to the tmux session.
        In case the session of that name already existed, then it opens a terminal and and attaches to it.

        Parameters:
            commands (dictionary): specifies the structure the tmux session will have; each key in the dictionary is the name of a window, and each value is expected to be a list, where each element is a string of a command to run in that window
            session_name (string, optional): name of the tmux session
            auto_attach (bool, optional): if True, it will open a terminal and attach to the tmux session; if False, it will only create the tmux session but not attach to it

        Example:
            sh.launch_tmux_from_dict(
                {
                    "sens&est": [
                        "ros2 launch robot_bringup robot_sensors.launch",
                        "ros2 launch robot_bringup robot_estimation.launch",
                        "ros2 launch robot_bringup robot_safety.launch",
                    ],
                }
            )
        """

        try:
            # The "has-session" command generates a CommandError exception if the session didn't not yet exist
            cls.execute(f'tmux has-session -t "{session_name}"')
            session_existed = True

            if not auto_attach:
                LogManager.info(
                    f"Session {session_name} already exists, not attaching to it"
                )
                return
        except CommandError:
            session_existed = False

            # Start a new tmux session
            cls.execute(f'tmux new-session -d -s "{session_name}"')

            # Enable mouse control
            cls.execute("tmux set -g mouse on")

            # Create tmux windows and run the commands
            for window_index, (window_name, window_commands) in enumerate(
                commands.items(), start=1
            ):
                # Create tmux windows
                if window_index == 1:
                    cls.execute(
                        f'tmux rename-window -t "{session_name}:1" "{window_name}"'
                    )
                else:
                    cls.execute(
                        f'tmux new-window -t "{session_name}" -n "{window_name}"'
                    )

                # Create tmux panes and run the commands
                for pane_index, pane_command in enumerate(window_commands, start=1):
                    # Run the command
                    cls.execute(
                        f'tmux send-keys -t "{session_name}:{window_index}.{pane_index}" "{pane_command}" C-m'
                    )

                    # If it is not the last command of the window
                    if pane_index < len(window_commands):
                        # Split the window
                        cls.execute(
                            f'tmux split-window -t "{session_name}:{window_index}" -h'
                        )

                # If there are more than two commands on the window, set the layout to "tiled"
                if len(window_commands) > 2:
                    cls.execute(
                        f"tmux select-layout -t {session_name}:{window_index} tiled"
                    )

        if auto_attach:
            # Check if there is an SSH connection
            if Settings.is_ssh_config_set():
                try:
                    # Open terminal and attach to remote tmux session
                    cls.open_terminal(
                        f'ssh {Settings.current_device.ssh_config.username}@{Settings.current_device.ssh_config.networks[Settings.current_device.ssh_config.selected_network].ip} -t tmux attach-session -t "{session_name}"'
                    )
                except Exception as e:
                    raise e
            else:
                # Open terminal and attach to local tmux session
                cls.open_terminal(f'tmux attach -t "{session_name}"')

        if session_existed:
            LogManager.info(
                f"Attached to previously existing "
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name}"'
            )
        else:
            LogManager.info(
                f"Created "
                + ("and attached to " if auto_attach else "")
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name}"'
            )


    @classmethod
    def launch_tmux(
        cls, commands: List[TmuxPaneCommand], session_name: str = "BirdWatch",
            pre_launch_cmd: str= ""
    ):
        """
        Creates a tmux session and opens windows and panes running commands on
        them as specified by "commands"; and then opens a terminal and attaches to the
        tmux session.

        In case the session of that name already existed, then it opens a terminal and
        and attaches to it.

        Parameters:
            commands (list[TmuxPaneCommand]): specifies the commands to be executed
            (in the order they appear in the list) and in which window they will be
            executed
            session_name (string, optional): name of the tmux session
        """

        try:
            # The "has-session" command generates a CommandError exception if the session didn't not yet exist
            cls.execute(f'tmux has-session -t "{session_name}"')

            session_existed = True
        except CommandError:
            session_existed = False

            # Start a new tmux session
            cls.execute(f'tmux new-session -d -s "{session_name}"')

            # Enable mouse control
            cls.execute("tmux set -g mouse on")

            # Get list of windows
            windows = list(OrderedDict.fromkeys(command.window for command in commands))
            windows_dict = {}

            # Create windows
            for index, window in enumerate(windows, start=1):
                if index == 1:
                    cls.execute(f'tmux rename-window -t "{session_name}:1" "{window}"')
                else:
                    cls.execute(f'tmux new-window -t "{session_name}" -n "{window}"')
                windows_dict[window] = {"index": index, "pane_qty": 0}

            for command in commands:
                # If it is not the first command of the window, split it
                if windows_dict[command.window]["pane_qty"] > 0:
                    cls.execute(
                        f'tmux split-window -t "{session_name}:{windows_dict[command.window]["index"]}" -h'
                    )
                windows_dict[command.window]["pane_qty"] += 1

                # If there are more than two commands on the window, set the layout to "tiled"
                if windows_dict[command.window]["pane_qty"] > 2:
                    cls.execute(
                        f'tmux select-layout -t {session_name}:{windows_dict[command.window]["index"]} tiled'
                    )


                # Run a command before the actual one
                if pre_launch_cmd:
                    cls.execute(
                        f'tmux send-keys -t "{session_name}:{windows_dict[command.window]["index"]}.{windows_dict[command.window]["pane_qty"]}" "{pre_launch_cmd}" C-m'
                    )
                # Run the command
                cls.execute(
                    f'tmux send-keys -t "{session_name}:{windows_dict[command.window]["index"]}.{windows_dict[command.window]["pane_qty"]}" "{command.command}" C-m'
                )

                if command.delay_ms > 0:
                    sleep(command.delay_ms / 1000)

        # Open terminal and attach to tmux session
        cls.open_terminal(f'tmux attach -t "{session_name}"')

        if session_existed:
            LogManager.info(
                f"Attached to previously existing "
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name}"'
            )
        else:
            LogManager.info(
                f"Created and attached to "
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name}"'
            )

    @classmethod
    def stop_tmux(
        cls, session_name: str = "BirdWatch"
    ):
        """
        Creates a tmux session and opens windows and panes running commands on
        them as specified by "commands"; and then opens a terminal and attaches to the
        tmux session.

        In case the session of that name already existed, then it opens a terminal and
        and attaches to it.

        Parameters:
            commands (list[TmuxPaneCommand]): specifies the commands to be executed
            (in the order they appear in the list) and in which window they will be
            executed
            session_name (string, optional): name of the tmux session
        """

        try:
            # The "has-session" command generates a CommandError exception if the session didn't not yet exist
            cls.execute(f'tmux has-session -t "{session_name}"')

            session_existed = True

            cls.execute(f'tmux kill-session -t "{session_name}"')
        except CommandError:
            session_existed = False

        if session_existed:
            LogManager.info(
                f"Attached to previously existing "
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name} and stopped it"'
            )
        else:
            LogManager.info(
                f"Tmux session did not exist: "
                + ("remote " if Settings.is_ssh_config_set() else "")
                + f'Tmux session "{session_name}"'
            )