#!/usr/bin/python
# ---------------------------------------------------------------------------------------------------------------------
# ComMetpy.py
#
# Author      : Peter Heijligers
# Description : Compare Methods
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2022-08-03 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
import os

from src.BL.CompareManager import CompareManager
from src.DL.Model import Model
from src.GL.BusinessLayer.ConfigManager import CF_OUTPUT_BASE_DIR, Singleton, CF_REPO_DIRS_SOPH, CF_LIST_DIFF_ONLY, \
    CF_FILE_NAME
from src.GL.BusinessLayer.LogManager import Singleton as Log
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import EMPTY
from src.GL.Enums import BLUE, GREEN
from src.GL.Functions import replace_root_in_path
from src.GL.GeneralException import GeneralException
from src.GL.Result import Result

session: Session
CM = Singleton()
model = Model()
log = Log()


class ComMetpy(object):

    @property
    def error_message(self):
        return self._error_message

    def __init__(self, output_dir=None):
        self._output_dir = output_dir
        self._unit_test = False
        self._error_message = None

    def start(self, unit_test=False) -> Result:
        """
        Main line
        """
        self._unit_test = unit_test
        self._configure_session()

        # Start _log
        self._start_log()

        # Go!
        compare_manager = CompareManager()
        return compare_manager.compare()

    def _configure_session(self):
        global session
        session = Session()
        # Get suffix output path
        suffix = None
        if CM.get_config_item(CF_FILE_NAME):
            suffix, _ = os.path.splitext(CM.get_config_item(CF_FILE_NAME))
        session.set_paths(self._unit_test, CM.get_config_item(CF_OUTPUT_BASE_DIR), restart_session=True, suffix=suffix)

    def _start_log(self):
        if not os.path.isdir(session.output_dir):
            raise GeneralException(f'Log directory "{session.output_dir}" is not valid.')

        log.start_log()

        log.stripe()
        self._log("src - Compare Methods", GREEN)
        log.stripe()
        self._log("File name  . . . . . . . . . . . . . . . . . : ", BLUE, new_line=False)
        self._log(CM.config_dict[CF_FILE_NAME])
        self._log("Repositories . . . . . . . . . . . . . . . . : ", BLUE, new_line=False)
        self._log(str(CM.config_dict[CF_REPO_DIRS_SOPH]))
        self._log("List differences only  . . . . . . . . . . . : ", BLUE, new_line=False)
        self._log(str(CM.config_dict[CF_LIST_DIFF_ONLY]))
        self._log("Output directory . . . . . . . . . . . . . . : ", BLUE, new_line=False)
        self._log(replace_root_in_path(session.output_dir))
        log.stripe()

    def _log(self, line, color=EMPTY, new_line=True, error=False):
        log.add_coloured_line(line, color, new_line)
        if error:
            self._error_message = line
