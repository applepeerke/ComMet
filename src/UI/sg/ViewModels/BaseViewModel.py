#!/usr/bin/env python3
from datetime import datetime
from typing import Any

import PySimpleGUI as sg

from src.DL.Model import Model
from src.GL.BusinessLayer.ConfigManager import config_desc_dict, Singleton as ConfigManager
from src.GL.Const import EMPTY, NONE
from src.GL.Functions import format_date, is_stringed_list
from src.GL.GeneralException import GeneralException
from src.GL.Validate import toBool, normalize_dir
from src.UI.sg.Constants.Color import THEME, COLOR_TEXT_DISABLED, COLOR_BACKGROUND_DISABLED, COLOR_LABEL_DISABLED
from src.UI.sg.Functions import get_name_from_text, gui_name_types, gui_values

from src.UI.sg.Data.WTyp import WTyp
from src.UI.sg.Const import *

sg.theme( THEME )  # E.g. LightBrown3, 8, 13

model = Model()
CM: ConfigManager


class BaseViewModel( object ):

    @property
    def Layout(self):
        return self._layout

    @property
    def Max_col_width(self):
        return self._max_col_width

    @property
    def X_path(self):
        return self._x_path

    @property
    def Col_def(self):
        return self._col_def

    @property
    def Window_name(self):
        return self._window_name

    @property
    def Table_name(self):
        return self._table_name

    def __init__(self, window_name=None, table_name=None):
        global CM
        CM = ConfigManager()   # After getting LATEST
        self._layout = []
        self._max_col_width = 60
        self._col_def = {}
        self._x_path = 60
        self._window = None
        self._window_name = window_name
        self._table_name = table_name

    def label(self, name, x=X1, k=None, tip=None, text_color=None):
        key_name = k or name
        return sg.Text( self.get_label( name ), k=self.gui_key( key_name, WTyp.LA ),
                        size=(x, Y1), p=P1, tooltip=tip, text_color=text_color )

    @staticmethod
    def button(key, x=X1, font=None):
        return sg.Button( button_text=key, size=(x, Y1), p=P1, font=font )

    def multi_frame(self, key, content: list, title=EMPTY, border_width=0, relief=None, visible=True, p=P,
                    justify='right', expand_y=False, expand_x=False) -> list:
        elems = []
        for item in content:
            for i in range( len( item ) ):
                elems.append( item[i] )
        return [sg.Frame( title, [elems], k=self.gui_key( key, WTyp.FR ), p=p, border_width=border_width,
                          relief=relief, visible=visible, element_justification=justify, expand_x=expand_x,
                          expand_y=expand_y )]

    def frame(self, key, content: list, title=EMPTY, border_width=0, relief=None, visible=True, p=P, justify='left',
              expand_y=False, expand_x=False, font=FONT_HUGE) -> list:
        return [
            sg.Frame( title, content, k=self.gui_key( key, WTyp.FR ), p=p, border_width=border_width, relief=relief,
                      visible=visible, element_justification=justify, expand_x=expand_x, expand_y=expand_y, font=font )]

    def lbl_cal(self, key, x=X1, dft=None, expand_x=False, evt=True, date_format='%Y-%m-%d', m_d_y=None,
                disabled=False):
        """ label - input """
        # Unfortunately Screen Location parameter can not be set dynamically...
        if not dft:
            dft = datetime.now().strftime( date_format )
        elif dft == NONE:
            dft = None
        if dft and not m_d_y:
            date = format_date(dft, 'YMD')
            if date:
                m_d_y = (int(date[5:7]), int(date[8:10]), int(date[:4]))
        if not m_d_y:
            m_d_y = (None, None, None)
        result = [self.label( name=key, x=x, tip=get_tooltip( key ) ),
                  self._input_text( key, dft, x, evt, expand_x, disabled=disabled ),
                  sg.CalendarButton( 'Calendar', k=self.gui_key( key, WTyp.CA ), format=date_format,
                                     default_date_m_d_y=m_d_y, disabled=disabled, location=(0, 0))]
        return result

    def cbx(self, key, x=X1, dft: bool = False, evt=True, disabled=False):
        """ check box """
        result, dft = self._get_box_label_and_default( key, WTyp.CB, dft, x, disabled )
        return [sg.Checkbox(
            text=self.get_label( key ), k=self.gui_key( key, WTyp.CB ), default=dft, size=(x, Y1), enable_events=evt,
            p=P1 )]

    # Boxes with separate label

    # noinspection PyTypeChecker
    def inbox(self, key, x=X1, dft=None, expand_x=False, x2=X1, evt=True, folder_browse=False, file_browse=False,
              disabled=False):
        """ label - input - file/folder browse"""
        target = self.gui_key( key, WTyp.IN )
        result, dft = self._get_box_label_and_default( key, WTyp.IN, dft, x, disabled )
        result.append( self._input_text( key, dft, x2, evt, expand_x, disabled ) )
        if folder_browse:
            dft = get_valid_folder_name( key, dft )
            result.append( sg.FolderBrowse(
                target=target, initial_folder=dft, k=self.gui_key( f'{key}_BTN', WTyp.DB ), enable_events=evt ) )
        elif file_browse:
            dft = get_valid_folder_name( key, dft )
            result.append( sg.FileBrowse(
                target=target, initial_folder=dft, k=self.gui_key( f'{key}_BTN', WTyp.FB ), enable_events=evt ) )
        return result

    # noinspection PyTypeChecker
    def combo(self, key, items=None, x=X1, dft=None, evt=True, extra_label=None, extra_label_key=None,
              button_text=None, disabled=False):
        """ combo box """
        result, dft = self._get_box_label_and_default( key, WTyp.CO, dft, x, disabled )
        max_len = max(len(str(item)) for item in items) if items else 0
        result.append( sg.Combo( items, k=self.gui_key( key, WTyp.CO ), default_value=dft, enable_events=evt,
                                 readonly=disabled,
                                 size=(max(max(max_len, 30), min( len( items ), 10 )) ),
                                 text_color=COLOR_TEXT_DISABLED if disabled else None,
                                 background_color=COLOR_BACKGROUND_DISABLED if disabled else None,
                                 ))
        return self._add_extras( result, extra_label, extra_label_key, button_text )

    # noinspection PyTypeChecker
    def options(self, key, items=None, x=X1, dft=None, evt=True, extra_label=None, extra_label_key=None,
                button_text=None, dft_none_is_all=False, disabled=False):
        """ List box """
        result, dft = self._get_box_label_and_default( key, WTyp.LB, dft, x, disabled )
        default_values = items if dft_none_is_all else dft
        result.append( sg.Listbox(
            items, k=self.gui_key( key, WTyp.LB ), default_values=default_values, enable_events=evt,
            disabled=disabled, select_mode='extended', size=(None, min( len( items ), 10 )) ) )
        return self._add_extras( result, extra_label, extra_label_key, button_text )

    def get_label(self, text):
        if self._table_name:
            return self.get_desc( text ) or text
        return config_desc_dict.get( text ) or text

    def get_desc(self, att_name):
        att = model.get_att( self._table_name, att_name )
        return att.description if att and att.description else att_name

    # Private

    def _get_box_label_and_default(
            self, key, box_type, dft, x, disabled=False) -> (Any, list):
        """
        dft: Return Setting-value if "key" is the name of setting, or Passed value.
        """
        text_color = COLOR_LABEL_DISABLED if disabled else None
        self.set_gui_value_keys( key, box_type)
        value = get_setting( key )
        dft = dft if (value in (None, EMPTY) or is_stringed_list(value)) \
            else value  # value may be "False" in a check box, or a list in a combo box!
        return [self.label( name=key, x=x, tip=get_tooltip( key ), text_color=text_color )], dft

    def _add_extras(self, result, extra_label, extra_label_key=None, button_text=None) -> list:
        if extra_label:
            self.set_gui_value_keys( extra_label_key or extra_label, WTyp.LA )
            result.append( self.label( name=extra_label, k=extra_label_key ) )
        if button_text:
            result.append( self.button( button_text ) )
        return result

    def _input_text(self, key, dft=None, x=X1, evt=False, expand_x=False, disabled=False):
        evt = False if disabled else evt
        self.set_gui_value_keys( key, WTyp.IN)
        return sg.InputText( size=(x, Y1), k=self.gui_key( key, WTyp.IN ), default_text=dft, enable_events=evt,
                             p=P1,
                             expand_x=expand_x, disabled=disabled, disabled_readonly_text_color=COLOR_TEXT_DISABLED,
                             disabled_readonly_background_color=COLOR_BACKGROUND_DISABLED )

    def gui_key(self, text, prefix=EMPTY) -> str:
        name = get_name_from_text( text )
        if not name:
            return EMPTY
        k = f'{self._window_name}|{name}' if self._window_name else name
        k = f'{k}_{prefix}' if prefix else k
        gui_name_types[name] = prefix
        return k

    def set_gui_value_keys(self, k, widget_type):
        """ Keep only information (not labels etc) from SimpleGuiManager"""
        k = f'{self._window_name}|{k}' if self._window_name else k
        if k in gui_values and widget_type != gui_values[k]:
            raise GeneralException( f'{__name__}: Key "{k}" already exists as a gui-value.' )
        gui_values[k] = widget_type

    def key_of(self, k):
        k = f'{self._window_name}|{k}' if self._window_name else k
        if k not in gui_values:
            return k
        return self.gui_key( k, gui_values[k])

    def _set_disabled(self, window, widget_label, disabled=True):
        self._set_property( window, widget_label, disabled=disabled )

    def _set_visible(self, window, widget_label, visible=False):
        self._set_property( window, widget_label, visible=visible )

    def _set_property(self, window, widget_label, **kwargs):
        widget_type = gui_name_types.get( get_name_from_text( widget_label ) )
        if widget_type == WTyp.CO:
            if 'value' not in kwargs:
                window[self.gui_key( widget_label, WTyp.LA )].update( **kwargs )
            window[self.gui_key( widget_label, WTyp.CO )].update( **kwargs )
        elif widget_type == WTyp.IN:
            if 'value' not in kwargs:
                window[self.gui_key( widget_label, WTyp.LA )].update( **kwargs )
            window[self.gui_key( widget_label, WTyp.IN )].update( **kwargs )
        elif widget_type == WTyp.CA:
            if 'value' not in kwargs:
                window[self.gui_key( widget_label, WTyp.LA )].update( **kwargs )
            window[self.gui_key( widget_label, WTyp.CA )].update( **kwargs )
        elif widget_type == WTyp.CB:
            window[self.gui_key( widget_label, WTyp.CB )].update( **kwargs )
        elif widget_type == WTyp.LA:
            window[self.gui_key( widget_label, WTyp.LA )].update( **kwargs )
        elif widget_type == WTyp.FR:
            window[self.gui_key( widget_label, WTyp.FR )].update( **kwargs )
        else:
            raise GeneralException( f'{__name__}: Unsupported widget type "{widget_type}"' )


def get_tooltip(k):
    return CM.get_config_item_tooltip( k )


def get_setting(k):
    setting = CM.get_config_item( k )
    return toBool( setting ) \
        if setting and isinstance( setting, str ) and setting.lower() in ('yes', 'no', 'true', 'false') \
        else setting


def set_setting(k, value, must_exist=True):
    CM.set_config_item( k, value, must_exist )


def default(setting):
    return get_setting( setting )


def get_valid_folder_name(key, dft):
    if key.endswith( '_soph' ):
        key = key.rstrip( '_soph' )
        dft = get_setting( key )
    return normalize_dir( dft )
