import shutil
import stat
from pathlib import Path
from paramiko.sftp_client import SFTPClient
from paramiko.sftp_attr import SFTPAttributes
from os import stat_result
import time
from ShellCommands import ShellCommands as sh
from Settings import Settings
from typing import Union


class FileManager:
    sftp: SFTPClient = None
    _cancel_function: bool = None

    @classmethod
    def establish(cls):
        if sh.ssh is None:
            sh.establish_ssh()
        cls.sftp = sh.ssh.open_sftp()

        # Get the home directory
        stdin, stdout, stderr = sh.ssh.exec_command("echo ~/")
        cls.home_dir = stdout.read().decode("utf-8").strip()

    @classmethod
    def close(cls):
        if cls.sftp is not None:
            cls.sftp.close()
            cls.sftp = None
            cls.home_dir = None

    @classmethod
    def normalize_path(
        cls, path: str, force_local: bool = False, debug: bool = False
    ) -> str:
        """
        Normalizes a path to be used in the remote device

        Parameters:
            path (string): Path to normalize
            force_local (bool, optional): If True, normalizes the path for the local device

        Returns:
            string: Normalized path
        """
        # Convert Path objects to strings
        if isinstance(path, Path):
            path = str(path)

        if Settings.is_ssh_config_set() and not force_local:
            # Normalize the path for the remote device
            if hasattr(cls, "home_dir"):
                if path.startswith("~/"):
                    return path.replace("~/", cls.home_dir, 1)
        else:
            # Normalize the path for the local device
            if not hasattr(cls, "local_home_dir"):
                cls.local_home_dir = str(Path.home()) + "/"

            if path.startswith("~/"):
                return path.replace("~/", cls.local_home_dir, 1)

        return path

    @classmethod
    def list_contents(cls, path: str, type: str = None, force_local: bool = False):
        """
        Lists the contents of a directory

        Parameters:
            path (string): Path of the directory to list
            type (string, optional): Type of content to list. Can be "files", "directories" or None (in which case all contents are listed)
            force_local (bool, optional): If True, lists the contents of the local directory
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to list the contents of the directory in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Get content and sort by modification time
                contents = cls.sftp.listdir_attr(path)
                contents.sort(key=lambda x: x.st_mtime)
                contents = [elem.filename for elem in contents]

                if type == "files":
                    return [
                        file
                        for file in contents
                        if stat.S_ISREG(cls.sftp.stat(f"{path}/{file}").st_mode)
                    ]
                elif type == "directories":
                    return [
                        dir
                        for dir in contents
                        if stat.S_ISDIR(cls.sftp.stat(f"{path}/{dir}").st_mode)
                    ]
                else:
                    return contents

            except Exception as e:
                raise e
        else:
            try:
                contents = sorted(
                    (p for p in Path(path).iterdir()),
                    key=lambda x: x.stat().st_mtime if x.exists() else 0,
                )

                if type == "files":
                    return [
                        file.name
                        # Check if the element is a file
                        for file in contents
                        if file.is_file()
                    ]
                elif type == "directories":
                    return [
                        # Check if the element is a directory
                        dir.name
                        for dir in contents
                        if dir.is_dir()
                    ]
                else:
                    # List all contents
                    return [elem.name for elem in list(Path(path).iterdir())]
            except Exception as e:
                raise e

    @classmethod
    def list_files(cls, path: str, force_local: bool = False):
        """
        Lists the files in a directory

        Parameters:
            path (string): Path of the directory to list
            force_local (bool, optional): If True, lists the files in the local directory
        """
        return cls.list_contents(path, type="files", force_local=force_local)

    @classmethod
    def list_directories(cls, path: str, force_local: bool = False):
        """
        Lists the directories in a directory

        Parameters:
            path (string): Path of the directory to list
            force_local (bool, optional): If True, lists the directories in the local directory
        """
        return cls.list_contents(path, type="directories", force_local=force_local)

    @classmethod
    def exists(cls, path: str, force_local: bool = False):
        """
        Checks if a file or directory exists

        Parameters:
            path (string): Path of the file or directory to check
            force_local (bool, optional): If True, checks if the file or directory exists in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Check if the file or directory exists in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                cls.sftp.stat(path)
                return True
            except FileNotFoundError:
                return False
            except Exception as e:
                raise e
        else:
            # Check if the file or directory exists in the local device
            try:
                Path(path).stat()
                return True
            except FileNotFoundError:
                return False
            except Exception as e:
                raise e

    @classmethod
    def read_file(cls, path: str, as_binary: bool = False, force_local: bool = False):
        """
        Opens a file

        Parameters:
            path (string): Path of the file to open
            as_binary (bool, optional): If True, opens the file in binary mode
            force_local (bool, optional): If True, opens the file in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to open the file in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Open the file
                file = cls.sftp.open(path, "r")

                # Read the content
                if as_binary:
                    content = file.read()
                else:
                    content = file.read().decode("utf-8")

                # Close the file
                file.close()
            except Exception as e:
                raise e
        else:
            try:
                # Open the file
                file = Path(path).open("rb" if as_binary else "r")

                # Read the content
                content = file.read()

                # Close the file
                file.close()
            except Exception as e:
                raise e

        return content

    @classmethod
    def write_file(cls, path: str, content, force_local: bool = False):
        """
        Writes content to a file

        Parameters:
            path (string): Path of the file to write
            content: The content to write to the file
            force_local (bool, optional): If True, writes the file in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to write the file in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Ensure the destination directory exists
                cls.mkdir(str(Path(path).parent))

                # Open the file
                file = cls.sftp.open(path, "w")

                # Write the content
                file.write(content)

                # Close the file
                file.close()
            except Exception as e:
                raise e
        else:
            try:
                # Ensure the destination directory exists
                Path(path).parent.mkdir(parents=True, exist_ok=True)

                # Open the file
                with Path(path).open("w") as file:
                    file.write(content)

            except Exception as e:
                raise e

    @classmethod
    def delete_file(cls, path: str, force_local: bool = False):
        """
        Deletes a file

        Parameters:
            path (string): Path of the file to delete
            force_local (bool, optional): If True, deletes the file in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to delete the file in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Delete the file
                cls.sftp.remove(path)
            except Exception as e:
                raise e
        else:
            try:
                # Delete the file
                Path(path).unlink()
            except Exception as e:
                raise e

    @classmethod
    def delete_directory(
        cls, path: str, force: bool = False, force_local: bool = False
    ):
        """
        Deletes a directory

        Parameters:
            path (string): Path of the directory to delete
            force (bool, optional): If True, deletes the directory and its contents
            force_local (bool, optional): If True, deletes the directory in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        # Check the directories content
        dir_contents = cls.list_contents(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to delete the directory in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                if dir_contents:
                    # If the directory is not empty, check if force is True
                    if force:
                        # Delete the contents of the directory
                        for element in dir_contents:
                            if stat.S_ISDIR(cls.sftp.stat(f"{path}/{element}").st_mode):
                                cls.delete_directory(
                                    f"{path}/{element}", force=True, force_local=False
                                )
                            else:
                                cls.sftp.remove(f"{path}/{element}")
                    else:
                        raise Exception("Directory is not empty")

                # Delete the directory
                cls.sftp.rmdir(path)

            except Exception as e:
                raise e
        else:
            try:
                if dir_contents:
                    # If the directory is not empty, check if force is True
                    if force:
                        # Delete the contents of the directory
                        for element in dir_contents:
                            if Path(f"{path}/{element}").is_dir():
                                cls.delete_directory(
                                    f"{path}/{element}", force=True, force_local=True
                                )
                            else:
                                Path(f"{path}/{element}").unlink()
                    else:
                        raise Exception("Directory is not empty")

                # Delete the directory
                Path(path).rmdir()
            except Exception as e:
                raise e

    @classmethod
    def mkdir(cls, path: str, force_local: bool = False):
        """
        Creates a directory

        Parameters:
            path (string): Path of the directory to create
            force_local (bool, optional): If True, creates the directory in the local device
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to create the directory in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Check if the parent directory exists before creating it
                try:
                    cls.sftp.stat(str(Path(path).parent))
                except FileNotFoundError:
                    cls.mkdir(str(Path(path).parent))

                # Check if the directory exists before creating it
                try:
                    cls.sftp.stat(path)
                except FileNotFoundError:
                    cls.sftp.mkdir(path)
            except Exception as e:
                raise e
        else:
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise e

    @classmethod
    def rename(cls, old_path: str, new_path: str, force_local: bool = False):
        """
        Renames a file or directory

        Parameters:
            old_path (string): Path of the file or directory to rename
            new_path (string): New path of the file or directory
            force_local (bool, optional): If True, renames the file or directory in the local device
        """
        old_path = cls.normalize_path(old_path, force_local=force_local)
        new_path = cls.normalize_path(new_path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to rename the file or directory in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Rename the file or directory
                cls.sftp.rename(old_path, new_path)
            except Exception as e:
                raise e
        else:
            try:
                # Rename the file or directory
                Path(old_path).rename(new_path)
            except Exception as e:
                raise e

    @classmethod
    def copy_file(
        cls,
        src: str,
        dest: str,
        keep_original: bool = True,
        force_local: bool = False,
    ):
        """
        Copies a file

        Parameters:
            src (string): Path of the file to copy
            dest (string): Path of the destination file
            keep_original (bool, optional): If True, keeps the original file
            force_local (bool, optional): If True, copies the file in the local device
        """
        src = cls.normalize_path(src, force_local=force_local)
        dest = cls.normalize_path(dest, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Try to copy the file in the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Ensure the destination directory exists
                cls.mkdir(str(Path(dest).parent))

                if keep_original:
                    # Create local copy of the file
                    cls.sftp.get(src, "/tmp/tmpfile")

                    # Copy the local file to the destination
                    cls.sftp.put("/tmp/tmpfile", dest)

                    # Remove the local copy
                    Path("/tmp/tmpfile").unlink()

                else:
                    # Check if destination file exists
                    try:
                        cls.sftp.stat(dest)
                        # If it exists, remove it
                        cls.sftp.remove(dest)
                    except FileNotFoundError:
                        pass

                    # Copy the file
                    cls.sftp.rename(src, dest)

            except Exception as e:
                raise e
        else:
            try:
                # Ensure the destination directory exists
                Path(dest).parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy(src, dest)

                # Remove the original file
                if not keep_original:
                    Path(src).unlink()

            except Exception as e:
                raise e

    @classmethod
    def send_file(
        cls, src: str, dest: str, keep_original: bool = True, force_local: bool = False
    ):
        """
        Sends a file to the remote device

        Parameters:
            src (string): Local path of the file to send
            dest (string): Path of the destination file in the remote device
            keep_original (bool, optional): If True, keeps the original file
            force_local (bool, optional): If True, sends the file to the local device
        """
        src = cls.normalize_path(src, force_local=True)
        dest = cls.normalize_path(dest, force_local=force_local)

        # Copy the file to the remote device
        if Settings.is_ssh_config_set() and not force_local:
            # Try to send the file to the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                # Ensure the destination directory exists
                cls.mkdir(str(Path(dest).parent))

                # Check if destination file exists
                try:
                    cls.sftp.stat(dest)
                    # If it exists, remove it
                    cls.sftp.remove(dest)
                except FileNotFoundError:
                    pass

                # Send the file
                cls.sftp.put(src, dest)
            except Exception as e:
                raise e
        else:
            # Copy the file to the destination
            try:
                cls.copy_file(src, dest, keep_original=keep_original, force_local=True)
            except Exception as e:
                raise e

        # Remove the original file
        if not keep_original:
            Path(src).unlink()

    @classmethod
    def get_file(cls, src: str, dest: str, keep_original: bool = True):
        """
        Gets a file from the remote device

        Parameters:
            src (string): Path of the file in the remote device
            dest (string): Local path of the destination file
            keep_original (bool, optional): If True, keeps the original file
        """
        if not Settings.is_ssh_config_set():
            raise Exception("No SSH configuration set")

        if cls.sftp is None:
            cls.establish()

        # Ensure the destination directory exists
        Path(dest).parent.mkdir(parents=True, exist_ok=True)

        src = cls.normalize_path(src)
        dest = cls.normalize_path(dest, force_local=True)

        # Get the file
        cls.sftp.get(src, dest)

        # Remove the original file
        if not keep_original:
            cls.sftp.remove(src)

    @classmethod
    def get_attributes(
        cls, path: str, force_local: bool = False, human_readable: bool = False
    ) -> Union[SFTPAttributes, stat_result, dict]:
        """
        Gets the file attributes

        Parameters:
            path (string): Path of the file to get attributes from
            force_local (bool, optional): If True, gets the file attributes from the local device
            human_readable (bool, optional): If True, returns the attributes in human readable format

        Returns:
            SFTPAttributes or stat_result: File attributes. For remote files, the fields supported are: ``st_mode``, ``st_size``, ``st_uid``, ``st_gid``, ``st_atime``, and ``st_mtime``

            dict: File attributes in human readable format. The fields are: ``mode``, ``size``, ``uid``, ``gid``, ``last_access``, and ``mtime``
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            # Get the file attributes from the remote device
            try:
                if cls.sftp is None:
                    cls.establish()

                stats = cls.sftp.stat(path)

            except Exception as e:
                raise e

        else:
            # Get the file attributes from the local device
            try:
                stats = Path(path).stat()

            except Exception as e:
                raise e

        if not human_readable:
            return stats
        else:
            return cls.make_attributes_human_readable(stats)

    @classmethod
    def make_attributes_human_readable(
        cls, attributes: Union[SFTPAttributes, stat_result]
    ) -> dict:
        """
        Converts the file or directory attributes to human readable format

        Parameters:
            attributes (SFTPAttributes or stat_result): File or directory attributes

        Returns:
            dict: File or directory attributes in human readable format
        """
        # Convert the attributes to a dictionary
        stats_dict = {}

        # Convert the mode to human readable format
        stats_dict["mode"] = stat.filemode(attributes.st_mode)

        # Convert the size to human readable format
        if attributes.st_size < 1024:
            stats_dict["size"] = f"{attributes.st_size} B"
        elif attributes.st_size < 1024**2:
            stats_dict["size"] = f"{attributes.st_size / 1024:.2f} KB"
        elif attributes.st_size < 1024**3:
            stats_dict["size"] = f"{attributes.st_size / 1024 ** 2:.2f} MB"
        else:
            stats_dict["size"] = f"{attributes.st_size / 1024 ** 3:.2f} GB"

        # Add the user ID to the dictionary
        stats_dict["uid"] = attributes.st_uid

        # Add the group ID to the dictionary
        stats_dict["gid"] = attributes.st_gid

        # Convert the last access time to human readable format
        stats_dict["last_accessed"] = time.ctime(attributes.st_atime)

        # Convert the last modification time to human readable format
        stats_dict["last_modified"] = time.ctime(attributes.st_mtime)

        return stats_dict

    @classmethod
    def get_file_size(
        cls, path: str, force_local: bool = False, human_readable: bool = False
    ) -> Union[int, str]:
        """
        Gets the file size

        Parameters:
            path (string): Path of the file to get the size from
            force_local (bool, optional): If True, gets the file size from the local device
            human_readable (bool, optional): If True, returns the size in human readable format

        Returns:
            int or string: File size. If human_readable is True, the size is returned in human readable format (e.g. "1.23 MB"), else the size is returned in bytes (int)
        """
        if human_readable:
            return cls.get_attributes(
                path, force_local=force_local, human_readable=human_readable
            )["size"]
        else:
            return cls.get_attributes(
                path, force_local=force_local, human_readable=human_readable
            ).st_size

    @classmethod
    def get_directory_content_size(
        cls, path: str, force_local: bool = False, human_readable: bool = False
    ) -> Union[int, str]:
        """
        Gets the size of the contents of a directory

        Parameters:
            path (string): Path of the directory to get the size from
            force_local (bool, optional): If True, gets the size of the contents of the directory in the local device
            human_readable (bool, optional): If True, returns the size in human readable format

        Returns:
            int or string: Size of the contents of the directory. If human_readable is True, the size is returned in human readable format (e.g. "1.23 MB"), else the size is returned in bytes (int)
        """
        path = cls.normalize_path(path, force_local=force_local)

        if Settings.is_ssh_config_set() and not force_local:
            try:
                if cls.sftp is None:
                    cls.establish()
            except Exception as e:
                raise e

        cls._cancel_function = False
        size = 0

        # Get the size of the contents of the directory in the remote device
        for file in cls.list_files(path, force_local=force_local):
            if cls._cancel_function is True:
                cls._cancel_function = None
                raise Exception("Operation cancelled")
            size += cls.get_file_size(f"{path}/{file}", force_local=force_local)

        # Get the size of the contents of the directory
        for directory in cls.list_directories(path, force_local=force_local):
            if cls._cancel_function is True:
                cls._cancel_function = None
                raise Exception("Operation cancelled")
            try:
                size += cls.get_directory_content_size(
                    f"{path}/{directory}", force_local=force_local
                )
            except Exception as e:
                raise e

        if human_readable:
            if size < 1024:
                return f"{size} B"
            elif size < 1024**2:
                return f"{size / 1024:.2f} KB"
            elif size < 1024**3:
                return f"{size / 1024 ** 2:.2f} MB"
            else:
                return f"{size / 1024 ** 3:.2f} GB"
        else:
            return size

    @classmethod
    def cancel_function(cls) -> bool:
        """
        Cancels the current operation

        Returns:
            bool: True if the operation was cancelled, False otherwise
        """
        if cls._cancel_function is not None:
            cls._cancel_function = True
            return True
        else:
            return False
