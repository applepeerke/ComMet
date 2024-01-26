# ---------------------------------------------------------------------------------------------------------------------
# ConfigManager.py
#
# Author      : Peter Heijligers
# Description : Return the configuration (crisp.config) in a dictionary.
# If crisp.config does not exist, it is created with default properties.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-23 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
import json
import os

from ComMet import get_app_root_dir
from src.GL.Const import EMPTY, NONE, APP_NAME
from src.GL.Functions import list_to_string
from src.GL.GeneralException import GeneralException
from src.GL.Validate import normalize_dir, emptyNone
from appdirs import *

# Settings
CF_SETTINGS_PATH = 'CF_SETTINGS_PATH'
CF_DEBUG_METHOD_NAME = 'CF_DEBUG_METHOD_NAME'
CF_FILE_NAME = 'CF_FILE_NAME'
CF_REPO_DIR = 'CF_REPO_DIR'
CF_REPO_DIRS = 'CF_REPO_DIRS'
CF_REPO_DIRS_SOPH = 'CF_REPO_DIRS_SOPH'

CF_INPUT_PATH = 'CF_INPUT_PATH'
CF_INPUT_PATHS = 'CF_INPUT_PATHS'
CF_INPUT_PATHS_SOPH = 'CF_INPUT_PATHS_SOPH'
CF_OUTPUT_BASE_DIR = 'CF_OUTPUT_BASE_DIR'
CF_LIST_DIFF_ONLY = 'CF_LIST_DIFF_ONLY'
CF_AUTO_CLOSE_TIME_S = 'CF_AUTO_CLOSE_TIME_S'

configDict = {
    CF_SETTINGS_PATH: EMPTY,
    CF_OUTPUT_BASE_DIR: EMPTY,
    CF_INPUT_PATH: EMPTY,
    CF_INPUT_PATHS: EMPTY,
    CF_INPUT_PATHS_SOPH: EMPTY,

    CF_DEBUG_METHOD_NAME: EMPTY,
    CF_FILE_NAME: EMPTY,
    CF_REPO_DIR: EMPTY,
    CF_REPO_DIRS: EMPTY,
    CF_REPO_DIRS_SOPH: EMPTY,

    CF_LIST_DIFF_ONLY: True,
    CF_AUTO_CLOSE_TIME_S: 3,
}

config_desc_dict = {
    CF_SETTINGS_PATH: 'Settings folder',
    CF_DEBUG_METHOD_NAME: 'Debug method name',
    CF_FILE_NAME: 'File name (optional)',
    CF_REPO_DIR: 'Repository to compare',
    CF_REPO_DIRS_SOPH: 'Repositories selected',

    CF_INPUT_PATH: 'File to compare',
    CF_INPUT_PATHS_SOPH: 'Files selected',
    CF_OUTPUT_BASE_DIR: 'Output directory',
    CF_LIST_DIFF_ONLY: 'List different methods only',
    # Hidden
    CF_INPUT_PATHS: '-hidden-',
    CF_AUTO_CLOSE_TIME_S: 'Message box auto-close time',
}

configDictTooltip = {
    CF_SETTINGS_PATH: 'Settings path. Your user settings can be saved for next time (as a kind of cookie).',
    CF_AUTO_CLOSE_TIME_S: 'Message box auto-close time in seconds after a successful action. 0=Do not auto-close',
}


def get_desc(key):
    return config_desc_dict.get(key, "")


class Singleton:
    """ ConfigManager """

    class ConfigManager(object):

        @property
        def config_dict(self):
            return self._config_dict

        @property
        def file_name(self) -> str:
            return self._file_name

        @config_dict.setter
        def config_dict(self, value):
            self._config_dict = value

        def __init__(self):
            self._config_dict = configDict
            self._file_name = f'.PHTools_{APP_NAME.lower()}.json'
            self._persist = False

        def start_config(self, persist=False):
            self._persist = persist
            path = str(self.get_path())
            if not path:
                raise GeneralException(f'Configuration could not be initialized. Invalid path "{path}"')
            self.set_config_item(CF_SETTINGS_PATH, path)
            if not os.path.exists(path):
                self.write_config()
            if os.path.exists(path):
                self._config_dict = json.load(open(path, "rb"))
            else:
                raise GeneralException(f'Configuration could not be saved. Path does not exist: "{path}"')
            return

        def write_config(self):
            json.dump(self._config_dict, open(self.get_path(), "w"), indent=4)

        def get_config_item(self, key):
            return self._config_dict.get(key)

        def set_config_item(self, key, value, must_exist=True):
            """ If value is a list type, convert comma-separated string to list."""
            if not key or (must_exist and key not in self._config_dict):
                return
            if type(configDict[key]) == list:
                self._config_dict[key] = [
                    emptyNone(item.replace("\'", EMPTY).strip()) for item in list_to_string(value).split(',')]
            else:
                value = normalize_dir(value) if key.endswith('DIR') else value
                self._config_dict[key] = emptyNone(value)

        @staticmethod
        def get_config_item_tooltip(key):
            return configDictTooltip.get(key)

        def get_path(self) -> str:
            """
            Place "cookie" in App output dir if persistence asked for or "cookie" is already present there.
            Else place it in the app root.
            """
            dir_name = normalize_dir(user_data_dir(APP_NAME), create=True)
            path = f'{dir_name}{self._file_name}'
            return path if os.path.isfile(path) or self._persist \
                else f'{get_app_root_dir()}{self._file_name}'

        @staticmethod
        def _sanitize(config_dict) -> dict:
            for k, v in config_dict.items():
                if v == NONE:
                    config_dict[k] = EMPTY
            return config_dict

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.ConfigManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
