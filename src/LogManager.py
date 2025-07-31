import logging
import logging.config
import yaml
import datetime
from from_root import from_root
from pathlib import Path
from Widgets.LoggingTextbox import LoggingTextbox


class LogManager:
    textbox: LoggingTextbox = None

    @classmethod
    def init(cls, print_header: bool = True):
        """
        Initializes the logging, including loading the configuration
        and an initial log
        """

        # Load configuration
        with from_root("config/log_config.yaml").open("r") as log_file:
            config = yaml.safe_load(log_file)

        # Update paths to be absolute
        config = cls.update_paths(config, from_root())

        # Configure logging
        logging.config.dictConfig(config)

        # Initial log
        if print_header:
            logging.info("")
            logging.info("")
            logging.info("----------------------------------------------------")
            logging.info(
                f'     BirdWatch started on {datetime.datetime.now().strftime("%A %d-%m-%Y")}'
            )
            logging.info("----------------------------------------------------")
            logging.info("")

    @classmethod
    def update_paths(cls, config: dict, package_root: Path) -> dict:
        """
        Update paths in the logging configuration dictionary to be absolute paths.
        """
        for handler in config.get("handlers", {}).values():
            if "filename" in handler:
                handler["filename"] = package_root.joinpath(handler["filename"])
        return config

    @classmethod
    def set_textbox(cls, textbox: LoggingTextbox):
        """
        Set the textbox for logging
        """
        cls.textbox = textbox

    @classmethod
    def debug(cls, message: str):
        """
        Log a debug message
        """
        logging.debug(message)

    @classmethod
    def info(cls, message: str, show_in_textbox: bool = True):
        """
        Log an info message
        """
        logging.info(message)
        if cls.textbox and show_in_textbox:
            cls.textbox.add_line("- " + message, LoggingTextbox.LogLevels.INFO)

    @classmethod
    def warning(cls, message: str, show_in_textbox: bool = True):
        """
        Log a warning message
        """
        logging.warning(message)
        if cls.textbox and show_in_textbox:
            cls.textbox.add_line("- " + message, LoggingTextbox.LogLevels.WARNING)

    @classmethod
    def error(cls, message: str, show_in_textbox: bool = True):
        """
        Log an error message
        """
        logging.error(message)
        if cls.textbox and show_in_textbox:
            cls.textbox.add_line("- " + message, LoggingTextbox.LogLevels.ERROR)

    @classmethod
    def critical(cls, message: str):
        """
        Log a critical message
        """
        logging.critical(message)

    @classmethod
    def exception(cls, message: str):
        """
        Log an exception message
        """
        logging.exception(message)
