import os
from src.variables import *


class Config:
    def __init__(self) -> None:
        """initialize the configuration"""
        self.name = ""
        self.style = 0
        self.controls = CONTROLS
        self.find_path()

    def find_path(self):
        """find the path of the config files for linux, windows and macos"""
        if os.name == "posix":
            self.dir = os.path.expanduser("~/.config/space-invaders")
            self.path = self.dir + "/config.txt"
        elif os.name == "nt":
            self.dir = os.path.expanduser("~\\AppData\\Roaming\\space-invaders")
            self.path = self.dir + "\\config.txt"
        elif os.name == "mac":
            self.dir = os.path.expanduser(
                "~/Library/Application Support/space-invaders"
            )
            self.path = self.dir + "/config.txt"

    def get(self) -> bool:
        """get the configuration from the .config.txt file if it exists"""
        try:
            with open(self.path, "r") as config_file:
                config = eval(config_file.readline().strip())
                self.name = config["name"]
                self.style = config["style"]
                self.controls = config["controls"]
                return True
        except:
            return False

    def save(self) -> None:
        """save the configuration to the .config.txt file"""
        if self.name == "":
            return
        # create the directory if it doesn't exist
        if not os.path.isfile(self.path):
            os.makedirs(self.dir, exist_ok=True)
        # write the configuration to the file
        with open(self.path, "w") as config_file:
            config = {"name": self.name, "style": self.style, "controls": self.controls}
            config_file.write(str(config))
