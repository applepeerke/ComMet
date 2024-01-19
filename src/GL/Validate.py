# ---------------------------------------------------------------------------------------------------------------------
# Validate.py
#
# Author      : Peter Heijligers
# Description : Validation functions
#
# - normalize_dir = validate a directory name for different platforms.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-23 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

import os
import platform
import re
import string

from ComMet import slash
from src.GL.Const import BLANK, EMPTY, NONE
from src.GL.GeneralException import GeneralException

valid = False
current = False
file_chars = string.ascii_letters + string.digits

REGEX_ALPHA = re.compile( r'^[\w]+$' )
REGEX_ALPHA_NUM = re.compile( r'^[\w\d _\-]+$' )
REGEX_CNAME = re.compile( r'^[\w\d_$#@]+$' )
REGEX_DIRNAME = re.compile( r'^[\w\d \-.:+@\\/_]+$' )  # ":" is allowed for windows drive
REGEX_FILENAME = re.compile( r'^[\w\d \-.%+_]+$')

PGM = 'Validate'


def normalize_dir(dir_name, create=False):
    if not dir_name:
        return EMPTY
    if create and not os.path.isdir(dir_name):
        try:
            os.makedirs(dir_name)
        except NotADirectoryError:
            raise
    return dir_name if dir_name[-1] in ('/', '\\') else f'{dir_name}{slash()}'


def _get_existing_dir(dir_name, create=False):
    while not os.path.exists(dir_name):
        try:
            dir_name = _get_dir_name( dir_name, create )
        except NotADirectoryError:
            return None
        if not os.path.exists(dir_name):
            return None
        break
    return dir_name


def _get_dir_name(dir_name, create=False):
    if create:
        try:
            os.makedirs(dir_name)
        except NotADirectoryError:
            raise GeneralException(f'{PGM}._get_dir_name: "{dir_name}" is not a directory')
    else:
        dir_name = EMPTY
    dir_name = _substitute_current_dir( dir_name )
    return dir_name


def _substitute_current_dir(dir_name):
    global current
    if not dir_name:
        return EMPTY

    if dir_name in ['/', './', '/.', '\\']:
        current = True
        dir_name = _format_dir( os.getcwd() )
    if str(dir_name).startswith('.'):
        dir_name = _format_dir( os.getcwd() + dir_name[1:] )
    return dir_name


def _format_dir(dir_name):
    if not dir_name:
        return EMPTY
    # Append a directory separator if not already present.
    if not (dir_name.endswith( '/' ) or dir_name.endswith('\\')):
        dir_name += '/'
    return format_os(dir_name)


def format_os(path_part):
    # On Windows, use backslash.
    if platform.system() == 'Windows':
        path_part = str(path_part).replace('/', '\\')
    else:
        path_part = str( path_part ).replace( '\\', '/' )
    return path_part


def os_slash():
    return format_os('/')


def isValidName(name, blank_allowed=False) -> bool:
    if not name:
        return False

    if len(name) > 64:
        name = name[:64]
    # Max. 64 chars without leading/trailing hyphen
    if not REGEX_ALPHA_NUM.fullmatch( name ):
        return False
    if not blank_allowed and BLANK in name:
        return False
    if name.startswith('-') or name.endswith('-'):
        return False
    return True

    # if blank_allowed:
    #     allowed = re.compile("(?!-)[A-Z_ \d-]{1,64}(?<!-)$", re.IGNORECASE)
    # else:
    #     allowed = re.compile("(?!-)[A-Z_\d-]{1,64}(?<!-)$", re.IGNORECASE)
    # while not all(allowed.fullmatch(x) for x in name):
    #     if ask:
    #         name = ui.ask("Name '" + name + "' is not valid. Please specify a valid name (q = quit): ")
    #     else:
    #         name = QUIT
    #     if name == QUIT:
    #         break
    # return name


def toBool(value, default=False) -> bool:
    if isinstance(value, bool):
        return value
    elif isinstance(value, str):
        return False if value.lower() == 'false' else True
    else:
        return default


def isInt(value) -> bool:
    try:
        int( value )
        return True
    except ValueError:
        return False


def isAlpha(value, maxLen=0) -> bool:
    if not _validSize(value, maxLen):
        return False
    return True if REGEX_ALPHA.fullmatch(value) else False

    # allowed = re.compile( "^[A-Z]$", re.IGNORECASE )
    # while not all(allowed.fullmatch(x) for x in value):
    #     return False
    # return True


def isAlphaNumeric(value, maxLen=0) -> bool:
    if not _validSize(value, maxLen):
        return False
    return True if REGEX_ALPHA_NUM.fullmatch(value) else False

    # allowed = re.compile( "^[A-Z_ \d-]$", re.IGNORECASE )
    # while not all(allowed.fullmatch(x) for x in value):
    #     return False
    # return True


def isName(value) -> bool:
    if not value:
        return False
    return True if REGEX_CNAME.fullmatch(value) else False
    # allowed = re.compile( "^[A-Z_$#@\d]$", re.IGNORECASE )
    # while not all(allowed.fullmatch(x) for x in value):
    #     return False
    # return True


def isDirname(value, maxLen=0) -> bool:
    if not _validSize(value, maxLen):
        return False
    return True if REGEX_DIRNAME.fullmatch(value) else False


def isFilename(value, maxLen=0) -> bool:
    if not _validSize(value, maxLen):
        return False
    return True if REGEX_FILENAME.fullmatch(value) else False


def _validSize(value, maxLen) -> bool:
    if not value or 0 < maxLen < len( value ):
        return False
    return True


def emptyNone(value):
    return EMPTY if value is None or value == NONE else value
