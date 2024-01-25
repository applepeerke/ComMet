# ---------------------------------------------------------------------------------------------------------------------
# SessionManager.py
#
# Author      : Peter Heijligers
# Description : Log a line
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

import datetime

from appdirs import *

from ComMet import get_root_dir, get_app_root_dir
from src.GL.Const import RESULTS_DIR, BASE_OUTPUT_SUBDIR, EMPTY, APP_NAME
from src.GL.GeneralException import GeneralException
from src.GL.Validate import normalize_dir


class Singleton:
    """ Singleton """

    class SessionManager:
        """Implementation of Singleton interface """

        @property
        def unit_test(self):
            return self._unit_test

        @property
        def debug_method_name(self):
            return self._debug_method_name

        @property
        def db(self):
            return self._db

        @property
        def db_name(self):
            return self._db_name

        @property
        def db_dir(self):
            return self._db_dir

        @property
        def suffix(self):
            return self._suffix

        @property
        def base_dir(self):
            return self._base_dir

        @property
        def has_db(self):
            return self._has_db

        @property
        def output_base_dir(self):
            return self._output_base_dir

        @property
        def output_dir(self):
            return self._output_dir

        @property
        def database_dir(self):
            return self._database_dir

        @property
        def resources_dir(self):
            return self._resources_dir

        @property
        def images_dir(self):
            return self._images_dir

        # Setters
        @unit_test.setter
        def unit_test(self, value):
            self._unit_test = value

        @debug_method_name.setter
        def debug_method_name(self, value):
            self._debug_method_name = value

        @database_dir.setter
        def database_dir(self, value):
            self._database_dir = value

        @db.setter
        def db(self, value):
            self._db = value

        @db_name.setter
        def db_name(self, value):
            self._db_name = value

        def __init__(self):
            """
            Constructor
            """
            self._debug_method_name = EMPTY
            self._base_dir = EMPTY
            self._output_base_dir = EMPTY
            self._output_dir = EMPTY
            self._db_dir = None
            self._has_db = False
            self._db = None
            self._database_dir = None
            self._db_name = f'{APP_NAME}.db'
            self._suffix = EMPTY
            self._unit_test = False
            self._resources_dir = None
            self._images_dir = None
            self._isStarted = False
            try:
                from src.DL.DBDriver.DBDriver import DBDriver
                self._has_db = True
            except ImportError or ModuleNotFoundError:
                self._has_db = False

        def set_paths(self, unit_test=False, output_dir=None, suffix=None, restart_session=False):
            # Suffix changed: restart session.
            if suffix and not self._suffix \
                    or (suffix and self._suffix and suffix not in self._suffix):
                restart_session = True

            if self._isStarted and not restart_session:
                return

            self._unit_test = unit_test
            self._output_base_dir = output_dir or normalize_dir(user_data_dir(APP_NAME), create=True)

            # Pgm dir
            root_dir = get_root_dir()
            self._base_dir = get_app_root_dir()
            if not self._base_dir:
                raise GeneralException(f'{__name__}: No app root dir found.')
            self._resources_dir = normalize_dir(f'{self._base_dir}resources')
            self._images_dir = normalize_dir(f'{self._resources_dir}images')

            # Output base dir
            # (Results, database) should be kept outside the program (src) directory
            if not self._output_base_dir or self._output_base_dir in self._base_dir:
                raise GeneralException(f'{__name__}: Invalid output folder "{self._output_base_dir}"')

            # Database dir
            self._database_dir = normalize_dir(f'{self._output_base_dir}UT', create=True) if unit_test else \
                normalize_dir(f'{self._output_base_dir}Data', create=True)

            # Output subdir
            subdir = RESULTS_DIR if not unit_test else f'{RESULTS_DIR}_UnitTest'
            output_subdir = normalize_dir(f'{self._output_base_dir}{subdir}', create=True)
            if not output_subdir:
                return
            extra_suffix = f'_{suffix}' if suffix else EMPTY
            self._suffix = f'{BASE_OUTPUT_SUBDIR}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}{extra_suffix}'
            self._output_dir = normalize_dir(f'{output_subdir}{self._suffix}', create=True)
            self._isStarted = True

    # ---------------------------------------------------------------------------------------------------------------------
    # Singleton logic
    # ---------------------------------------------------------------------------------------------------------------------

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.SessionManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
