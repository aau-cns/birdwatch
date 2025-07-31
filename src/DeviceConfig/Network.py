import re


class Network:
    def __init__(self, name: str, ip: str):
        self.update(name, ip)

    def update(self, name: str = None, ip: str = None):
        if name is None:
            name = self.name
        else:
            if name == "":
                raise ValueError("Name cannot be empty")

        if ip is None:
            ip = self.ip
        else:
            if not self.is_valid_ip(ip):
                raise ValueError("Invalid IP address format")

        self.name = name
        self.ip = ip

    @staticmethod
    def is_valid_ip(ip: str):
        """
        Checks if the IP has the correct format ('X.X.X.X', where each
        'X' is a number between 0 and 255)
        """
        pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        return re.match(pattern, ip) is not None

    def to_dictionary(self) -> dict:
        return {"name": self.name, "ip": self.ip}
