import os

import PySimpleGUI as sg

from src.GL.Functions import get_icon
from src.GL.Validate import normalize_dir
from src.UI.sg.Const import FONT, CMD_OK
from src.UI.sg.Data.WTyp import WTyp
from src.UI.sg.Functions import get_name_from_key, get_name_from_text

from src.UI.sg.General.Boxes import info_box
from src.UI.sg.ViewModels.BaseViewModel import set_setting, BaseViewModel
from src.GL.BusinessLayer.ConfigManager import config_desc_dict, Singleton as ConfigManager
from src.GL.Const import EMPTY

CM = ConfigManager()


class InputBox(BaseViewModel):

    def __init__(self):
        super().__init__()

    def get_input(self, label, title, dft=None) -> str:
        if not label:
            return EMPTY
        return self._process_box(label, title, dft=dft)

    def set_folder_in_config(self, key) -> bool:
        """ Key: E.g. CF_OUTPUT_DIR """
        dft = CM.get_config_item(key) or EMPTY
        input_value = self._process_box(key, f'Select {config_desc_dict[key]}', folder_browse=True, dft=dft)
        if input_value and os.path.isdir(input_value):
            set_setting(key, normalize_dir(input_value), must_exist=False)
            return True
        return False

    def set_path_in_config(self, key) -> bool:
        """ Key: E.g. CF_FILE_PATH """
        dft = CM.get_config_item(key) or EMPTY
        input_value = self._process_box(key, f'Select {config_desc_dict[key]}', file_browse=True, dft=dft)
        if input_value and os.path.isfile(input_value):
            set_setting(key, input_value, must_exist=False)
            return True
        return False

    def _process_box(self, key, window_title, folder_browse=False, file_browse=False, dft=EMPTY) -> str:
        """ A value is required, unless the box window is closed. """
        window = sg.Window(window_title, self._get_view(key, folder_browse, file_browse, dft),
                           font=FONT, alpha_channel=.98, text_justification='left',
                           resizable=True, finalize=True, icon=get_icon())

        while True:
            event, values = window.read()  # type: str, dict
            if event == sg.WIN_CLOSED:
                input_value = EMPTY
                break

            event_key = get_name_from_key(event) or get_name_from_text(event)

            # Handle button click
            if event_key == get_name_from_text(CMD_OK):
                input_value = values.get(self.gui_key(key, WTyp.IN))
                if folder_browse and not os.path.isdir(input_value):
                    info_box( 'Directory does not exist.' )
                    continue
                if file_browse and not os.path.isfile(input_value):
                    info_box( 'File does not exist.' )
                    continue
                if input_value:
                    break

        window.close()
        return input_value

    def _get_view(self, gui_key, folder_browse=False, file_browse=False, dft=None) -> list:
        x = len(self.get_label(gui_key))
        x2 = len(dft) if dft else None
        return [
            [self.inbox(gui_key, dft=dft, x=x, x2=x2, folder_browse=folder_browse, file_browse=file_browse)],
            [self.button(CMD_OK)],
        ]
