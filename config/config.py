from configparser import RawConfigParser

from utils import touch
from .const import *


class Config:
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

        self.__global_config = RawConfigParser()
        self.__bilibili = RawConfigParser()
        self.__translate = RawConfigParser()

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
        for section_name, options in GlobalTitleToOption.items():
            if not self.__global_config.has_section(section_name):
                self.__global_config.add_section(section_name)

            for _, option_name in options.items():
                if not self.__global_config.has_option(section_name, option_name):
                    self.__global_config.set(section_name, option_name, '')

        # Bilibili config
        for section_name, options in BilibiliTitleToOption.items():
            if not self.__bilibili.has_section(section_name):
                self.__bilibili.add_section(section_name)

            for _, option_name in options.items():
                if not self.__bilibili.has_option(section_name, option_name):
                    self.__bilibili.set(section_name, option_name, '')

        # Translate config
        for section_name, options in TranslateTitleToOption.items():
            if not self.__translate.has_section(section_name):
                self.__translate.add_section(section_name)

            for _, option_name in options.items():
                if not self.__translate.has_option(section_name, option_name):
                    self.__translate.set(section_name, option_name, '')

        self.save_config()

    def read_config(self):
        self.__global_config.read(CONFIG_ROOT + ConfigFile[EConfigType.Global])
        self.__bilibili.read(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili])
        self.__translate.read(CONFIG_ROOT + ConfigFile[EConfigType.Translate])

    def save_config(self):
        # global config
        file = open(CONFIG_ROOT + ConfigFile[EConfigType.Global], 'w')
        self.__global_config.write(file, space_around_delimiters=False)
        file.close()

        # bilibili config
        file = open(CONFIG_ROOT + ConfigFile[EConfigType.Bilibili], 'w')
        self.__bilibili.write(file, space_around_delimiters=False)
        file.close()

        # translate config
        file = open(CONFIG_ROOT + ConfigFile[EConfigType.Translate], 'w')
        self.__translate.write(file, space_around_delimiters=False)
        file.close()

    def update_config(self):
        pass