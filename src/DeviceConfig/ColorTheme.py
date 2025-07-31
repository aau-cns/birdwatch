import re


class ColorTheme:
    """
    Contains the primary color of a theme in three different shades.

    Args:
        primary (string): hexadecimal value of the primary color, in format "#XXXXXX".
        dark_primary (string): hexadecimal value of a dark shade of the primary color, in format "#XXXXXX".
        darker_primary (string): hexadecimal value of a darker shade of the primary color, in format "#XXXXXX".

    Raises:
        ValueError: If the one of the expected parameters doesn't have the format "#XXXXXX".

    Example:
        color_theme = ColorTheme("#1F6AA5", "#144870", "#203A4F")
    """

    __default_primary = "#2c6a98"
    __default_dark_primary = "#1e4766"
    __default_darker_primary = "#153248"

    def __init__(
        self,
        primary=__default_primary,
        dark_primary=__default_dark_primary,
        darker_primary=__default_darker_primary,
    ):
        if not self.is_valid_color(primary):
            raise ValueError("Invalid primary color format")
        if not self.is_valid_color(dark_primary):
            raise ValueError("Invalid dark primary color format")
        if not self.is_valid_color(darker_primary):
            raise ValueError("Invalid darker primary color format")

        self.primary = primary
        self.dark_primary = dark_primary
        self.darker_primary = darker_primary

    @staticmethod
    def is_valid_color(color):
        # Regular expression to match color format
        pattern = r"^#[0-9a-fA-F]{6}$"
        return re.match(pattern, color) is not None

    def is_default(self) -> bool:
        return (
            self.primary == self.__default_primary
            and self.dark_primary == self.__default_dark_primary
            and self.darker_primary == self.__default_darker_primary
        )

    def to_dictionary(self) -> dict:
        return {
            "primary": self.primary,
            "dark_primary": self.dark_primary,
            "darker_primary": self.darker_primary,
        }
