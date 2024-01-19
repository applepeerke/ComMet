# ---------------------------------------------------------------------------------------------------------------------
# Enums.py
#
# Author      : Peter Heijligers
# Description : Enums
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

RED = 'RED'
GREEN = 'GREEN'
ORANGE = 'ORANGE'
BLUE = 'BLUE'
PURPLE = 'PURPLE'
NC = 'NC'


class Color(object):
    RED = '\033[31m'
    GREEN = '\033[32m'
    ORANGE = '\033[33m'
    BLUE = '\033[36m'  # Was 34m
    PURPLE = '\033[35m'
    NC = '\033[0m'

    @staticmethod
    def toDict():
        return {RED: Color.RED,
                GREEN: Color.GREEN,
                ORANGE: Color.ORANGE,
                BLUE: Color.BLUE,
                PURPLE: Color.PURPLE,
                NC: Color.NC, }


# W10 does not seem to support ANSI cmd colors
class ColorWin(object):
    RED = ''
    GREEN = ''
    ORANGE = ''
    BLUE = ''
    PURPLE = ''
    NC = ''


class ErrType(object):
    Error = 'Error'
    Info = 'Info'
    Warning = 'Warning'
    Exception = 'Exception'
    SqlException = 'SqlException'


class LogType(object):
    File = 'File'
    Stdout = 'Stdout'
    Both = 'Both'


class LogLevel(object):
    Error = 'Error'
    Info = 'Info'
    Warning = 'Warning'
    Verbose = 'Verbose'
    All = 'All'


class ResultCode(object):
    Ok = 'OK'
    Error = 'ER'
    NotFound = 'NR'
    Equal = 'EQ'
    Cancel = 'CN'
    Warning = 'WA'


class MessageSeverity( object ):
    Info = 10
    Warning = 20
    Error = 30
    Completion = 40


class Appearance(object):
    Label = 'Label'
    OptionBox = 'OptionBox'
    CheckBox = 'CheckBox'
    RadioButton = 'RadioButton'
    Entry = 'Entry'
    TextArea = 'TextArea'
