from configparser import RawConfigParser

from utils import touch
from .const import *


class GlobalConfig:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(self):
        # create config file
        touch(CONFIG_ROOT + ConfigFile[EConfigType.Global])
        touch(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])
        touch(CONFIG_ROOT + ConfigFile[EConfigType.Translate])

        self.__global_config = Config(CONFIG_ROOT + ConfigFile[EConfigType.Global])
        self.__bilibili = Config(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])
        self.__translate = Config(CONFIG_ROOT + ConfigFile[EConfigType.Translate])

        self.read_config()
        self.__calibrate_config()

    @property
    def global_config(self):
        return self.__global_config

    @property
    def bilibili(self):
        return self.__bilibili

    @property
    def translate(self):
        return self.__translate

    def __calibrate_config(self):
        # global config
        self.__global_config.validate_config(GlobalTitleToOption)
        self.__bilibili.validate_config(BilibiliTitleToOption)
        self.__translate.validate_config(TranslateTitleToOption)

        self.save_config()

    def read_config(self):
        self.__global_config.read_config()
        self.__bilibili.read_config()
        self.__translate.read_config()

    def save_config(self):
        self.__global_config.save_config()
        self.__bilibili.save_config()
        self.__translate.save_config()

    def update_config(self):
        pass


class Config(RawConfigParser):

    def __init__(self, config_file:str):
        super().__init__()
        self.__config_file = config_file

    def read_config(self):
        self.read(self.__config_file)

    def save_config(self):
        file = open(self.__config_file, 'w')
        self.write(file, space_around_delimiters=False)
        file.close()

    def validate_config(self, title_to_options: dict):
        for section_name, options in title_to_options.items():
            if not self.has_section(section_name):
                self.add_section(section_name)

            for _, option_name in options.items():
                if not self.has_option(section_name, option_name):
                    self.set(section_name, option_name, '')