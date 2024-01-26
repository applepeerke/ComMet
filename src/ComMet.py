#!/usr/bin/env python3

import PySimpleGUI as sg

from src.GL.Functions import get_icon
from src.GL.BusinessLayer.ConfigManager import CF_REPO_DIRS_SOPH, CF_REPO_DIR
from src.GL.Const import APP_NAME
from src.GL.GeneralException import GeneralException
from src.UI.sg.Const import *
from src.UI.sg.Controller import Controller
from src.UI.sg.Functions import get_name_from_key, status_message, get_name_from_text
from src.UI.sg.ViewModels.MainViewModel import MainViewModel, set_setting

M = MainViewModel()
C = Controller()


def start():
    try:
        if C.start():
            _start_app()
        else:
            raise GeneralException
    # Exception handling
    except (GeneralException, Exception) as e:
        C.factory_reset(text=f'{APP_NAME} could not be started.\n\nReason: {e}\n')


def _start_app():
    window = sg.Window( 'C o m M e t - Compare methods', M.get_view(), font=FONT, alpha_channel=.98,
                        text_justification='left', icon=get_icon(),
                        resizable=True, finalize=True )
    window[EXPAND].expand( True, True, True )

    while True:
        event, values = window.read()  # type: str, dict
        event_key = get_name_from_key( event )
        # print( event, values )
        status_message( window )

        if event == sg.WIN_CLOSED:
            C.save_config()
            break
        set_setting( event_key, values.get( event ), must_exist=False )

        # Combo select
        if event_key == CF_REPO_DIRS_SOPH:
            window[M.key_of( CF_REPO_DIR )].update( C.get_dir_from_soph( values.get( event ) ) )

        # Button clicks
        if event == CMD_START:
            C.run()
            status_message( window, C.Result )
        elif event == CMD_FACTORY_RESET:
            C.factory_reset()
        # - Repos
        elif event == CMD_ADD_REPO:
            C.add_repo_dir( )
            C.update_repo_paths_soph(window, M)
            status_message( window, C.Result )
        elif event == CMD_DELETE_REPO:
            C.remove_repo_dir( )
            C.update_repo_paths_soph(window, M)
            status_message( window, C.Result )
        elif event == CMD_CLEAR_REPO:
            C.clear_repo_dirs( )
            C.update_repo_paths_soph(window, M)
            status_message( window, C.Result )

    window.close()


if __name__ == '__main__':
    start()
