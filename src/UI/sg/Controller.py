import shutil
import sys

from src.BL.CompareManager import CompareManager
from src.BL.DebugManager import Singleton as DebugManager
from src.ComMetpy import ComMetpy
from src.GL.BusinessLayer.ConfigManager import *
from src.GL.BusinessLayer.ConfigManager import Singleton as ConfigManager
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import DONE
from src.GL.Enums import MessageSeverity, ResultCode
from src.GL.GeneralException import GeneralException
from src.GL.Result import Result
from src.UI.sg.Const import Q_DATABASE_CORRUPT, CMD_FACTORY_RESET
from src.UI.sg.Functions import confirmed
from src.UI.sg.General.Boxes import confirm, confirm_factory_reset, info_box
from src.UI.sg.General.InputBox import InputBox
from src.UI.sg.ViewModels.BaseViewModel import get_setting
from src.UI.sg.ViewModels.MessageBox import message_box

session = Session()
CM = ConfigManager()


class Controller(object):

    @property
    def Result(self):
        return self._result

    def __init__(self):
        self._result = Result()
        self._severity = MessageSeverity.Info
        self._messages = []
        self._session = None
        self._CmpM = None

    """
    Initial start-up
    """

    def start(self) -> bool:
        # Config
        # - Persist your settings (kind of "Cookie")?
        try:
            path = f'{normalize_dir(user_data_dir(APP_NAME), create=True)}{CM.file_name}'
            persist = os.path.isfile(path)
            if not persist and not CM.get_config_item(CF_SETTINGS_PATH):
                persist = confirm(f'Your {APP_NAME} settings will be saved (as a kind of cookie) in:\n\n'
                                  f'  o Folder name: {user_data_dir(APP_NAME)}\n'
                                  f'  o File name: {CM.file_name}\n',
                                  'Save your settings?')
            # - Start
            CM.start_config(persist)

            # - Output dir MUST exist.
            CM.set_config_item(CF_OUTPUT_BASE_DIR, user_data_dir(APP_NAME))
            self._set_required_config(CF_OUTPUT_BASE_DIR)

        except GeneralException:
            return False

        # Session
        session.set_paths(output_dir=CM.get_config_item(CF_OUTPUT_BASE_DIR))

        # DB
        if session.has_db:
            self._start_db()

        # Business logic
        self._CmpM = CompareManager()
        return self._result.OK

    @staticmethod
    def factory_reset(title=CMD_FACTORY_RESET, text=None):
        try:
            app_dir = normalize_dir(user_data_dir(APP_NAME))
            prefix = f'{text}\n' if text else EMPTY
            if confirm_factory_reset(f'{prefix}Do you want to reset {APP_NAME}?\n\n'
                                     f'The configuration and output will be removed. Folder is\n'
                                     f'{app_dir}',
                                     title):
                if os.path.isdir(app_dir):
                    shutil.rmtree(app_dir)
                    sys.exit(0)
                else:
                    info_box(f'Configuration and output was not removed. It was not found in "{app_dir}"')
        except Exception as e:
            print(str(e))
            sys.exit(0)

    def _set_required_config(self, config_item):
        self._made_changes = False
        dir_name = CM.get_config_item(config_item)
        if not dir_name or not os.path.isdir(dir_name):
            InputBox().set_folder_in_config(config_item)
            self._made_changes = True
        # Retry
        dir_name = CM.get_config_item(config_item)
        if not dir_name or not os.path.isdir(dir_name):
            raise GeneralException(
                f'Required configuration item "{config_desc_dict.get(config_item)}" could not be set.')

    def _start_db(self):
        self._result = Result()

        if not session.has_db:
            return

        self._check_DB()

        if not self._result.OK:
            if confirmed(self._result):  # Rebuild db confirmed?
                self._check_DB()
                if not self._result.OK:
                    return

        from src.UI.DataDriver import DataDriver
        self._data_driver = DataDriver(session.db)

    def _check_DB(self):
        if not session.has_db:
            self._result = Result(ResultCode.Ok, 'DB is not supported.')
            return

        from src.DL.DBInitialize import DBInitialize
        # a. Connect
        code = ResultCode.Ok
        dbInit = DBInitialize()
        if not dbInit.connect():
            self._result = Result(ResultCode.Error, messages=dbInit.messages)
            return

        # b. Consistent? Then ok.
        if dbInit.is_consistent():
            self._result = Result(code, 'DBDriver is consistent.')
            return

        # c. Show the error messages and ask for Rebuild.
        code = ResultCode.Error
        error_text = '\n'.join(str(m) for m in dbInit.messages)
        if message_box(error_text, cont_text='Force rebuild', title=Q_DATABASE_CORRUPT):
            # yes, rebuild and recheck consistency.
            if dbInit.is_consistent(force=True):
                code = ResultCode.Ok
            # self._result = Result( code, text=title, messages='\n'.join( str( m ) for m in dbInit.messages ) )
            self._result = Result(code, text='DBDriver rebuild result', messages=dbInit.messages)

    """
    Run
    """

    @staticmethod
    def save_config():
        CM.write_config()

    def run(self):
        kwargs = dict(output_dir=get_setting(CF_OUTPUT_BASE_DIR), )
        session.debug_method_name = get_setting(CF_DEBUG_METHOD_NAME)

        try:
            commet = ComMetpy(**kwargs)
            self._result = commet.start()
            self._completion()
            if self._result.OK and session.debug_method_name:
                self._result = DebugManager().evaluate_first_3_methods()

        except SystemExit as e:
            message_box(e, severity=MessageSeverity.Error)

        self.save_config()

    def update_repo_paths_soph(self, window, M):
        # Combobox
        value = self._CmpM.repo_dirs_sophisticated[0] if len(self._CmpM.repo_dirs_sophisticated) > 0 else EMPTY
        window[M.key_of(CF_REPO_DIRS_SOPH)].update(value=value, values=self._CmpM.repo_dirs_sophisticated)
        # Config
        CM.set_config_item(CF_REPO_DIRS_SOPH, self._CmpM.repo_dirs_sophisticated)

    """
    Maintain paths
    """

    def _valid_input(self) -> bool:
        self._result = Result()
        base_dir = get_setting(CF_REPO_DIR)
        if not base_dir:
            self._result = Result(ResultCode.Error, text=f'{get_desc(CF_REPO_DIR)} is empty.')
            return False
        return True

    # Repo
    def add_repo_dir(self):
        if not self._valid_input():
            return
        self._result = self._CmpM.add_repo_dir(get_setting(CF_REPO_DIR))

    def remove_repo_dir(self):
        if not self._valid_input():
            return
        self._result = self._CmpM.remove_repo_dir(get_setting(CF_REPO_DIR))

    def clear_repo_dirs(self):
        self._result = self._CmpM.clear_repo_dirs()

    def get_dir_from_soph(self, path_soph):
        self._result = self._CmpM.get_dir_from_soph(path_soph)

    def _completion(self) -> list:
        if not self._result.OK:
            self._messages = self._result.messages or [self._result.text]
        elif not self._result.text:
            self._result = Result(text=DONE)
        return self._messages
