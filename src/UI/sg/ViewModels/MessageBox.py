# import os

import PySimpleGUI as sg

from src.GL.Functions import get_icon
from src.GL.BusinessLayer.ConfigManager import Singleton as ConfigManager, CF_AUTO_CLOSE_TIME_S
from src.GL.Const import BLANK
from src.GL.Enums import MessageSeverity
from src.UI.sg.Const import FONT, POPUP_WIDTH_MAX, POPUP_AUTO_CLOSE_DEFAULT
from src.GL.Validate import toBool, isInt
from src.GL.Functions import remove_color_code
from src.GL.GeneralException import GeneralException
from src.UI.sg.Constants.Color import *

CM = ConfigManager()


def message_box(message, cont_text=None, title=None, severity=MessageSeverity.Info, auto_close_duration=None) -> bool:
    if not message:
        raise GeneralException( f'{__name__}: Invalid input' )

    if not title:
        title = BLANK

    # icon = f'{Session().images_dir}Peer.ico'
    # icon = icon if os.path.isfile( icon ) else None

    message = remove_color_code( str( message ) )

    # Calculate width from the message
    max_length, count = 0, 0
    escape = False
    length = len(message)
    for i in range(length):
        if escape:
            escape = False
            if message[i] == 'n':
                max_length = count if count > max_length else max_length
                count = 0
        if message[i] == '\\':
            escape = True
        else:
            count += 1
    # Last time
    max_length = count if count > max_length else max_length
    width = max_length if 0 < max_length < POPUP_WIDTH_MAX else POPUP_WIDTH_MAX

    auto_close = False
    if auto_close_duration is not None and auto_close_duration == 0:
        value = auto_close_duration
    else:
        value = CM.get_config_item(CF_AUTO_CLOSE_TIME_S)
    auto_close_duration = int(value) if isInt(value) else POPUP_AUTO_CLOSE_DEFAULT

    # Continue?
    if cont_text:
        message = f'{message}\n\n{cont_text}?'
    # Button color
    if severity == MessageSeverity.Error:
        button_color = (BUTTON_COLOR_TEXT, COLOR_ERROR)
    elif severity == MessageSeverity.Warning:
        button_color = (BUTTON_COLOR_TEXT, COLOR_WARNING)
    elif severity == MessageSeverity.Info:
        button_color = (BUTTON_COLOR_TEXT, COLOR_OK)
        auto_close = True if auto_close_duration > 0 else False
    else:
        button_color = None

    if message.endswith( '?' ):
        # Question
        answer = sg.PopupYesNo( title, message, button_color=button_color, font=FONT, no_titlebar=True,
                                background_color=POPUP_COLOR_BACKGROUND, text_color=COLOR_TEXT, keep_on_top=True,
                                line_width=width, icon=get_icon())
        answer = toBool( answer )
        return answer
    else:
        # Not a question
        sg.Popup( title, message, button_color=button_color, font=FONT, no_titlebar=True,
                  background_color=POPUP_COLOR_BACKGROUND, text_color=COLOR_TEXT, keep_on_top=True,
                  auto_close=auto_close, auto_close_duration=auto_close_duration, line_width=width, icon=get_icon() )
        return False  # Do not confirm
