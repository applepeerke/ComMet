import PySimpleGUI as sg

from src.GL.Functions import get_icon
from src.UI.sg.Const import FONT


def confirm(text, title='Confirm') -> bool:
    answer = sg.PopupYesNo( text, title=title, grab_anywhere=True, keep_on_top=True, icon=get_icon(), font=FONT )
    return True if answer == 'Yes' else False


def info_box(text, title='Error'):
    sg.PopupOK( text, title=title, grab_anywhere=True, keep_on_top=True, icon=get_icon(), font=FONT  )


def confirm_factory_reset(text, title='Fatal error') -> bool:
    answer = sg.PopupOKCancel(text, title=title, keep_on_top=True, font=FONT)
    return True if answer == 'OK' else False
