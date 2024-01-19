import base64
import datetime
import ntpath
import os
import string
import time

from src.GL.Const import EMPTY, APOSTROPHES, NONE, BLANK, APP_NAME
from src.GL.Enums import Color, GREEN, RED
from src.GL.Validate import format_os, isInt

path_head = EMPTY
alphanum = string.ascii_letters + string.digits
loop_count = 0
suffix_p = None
date_zeroes = '0000000000'
DB_LIST_REPRESENTATION_SUBSTITUTE = ( '\'', '"', "\\'", ',' )


def sanitize_text(text: str, special_chars: tuple = ("'", "\n"), replace_by: str = "_") -> str:
    try:
        if not text:
            return EMPTY
        for c in special_chars:
            if c in text:
                text = str.replace(text, c, replace_by )
    except TypeError:  # Not a string: pass
        pass
    finally:
        return text
    # return "".join(c for c in special_chars if c in text)


def strip_bytes_and_crlf(line):
    # Remove byte presentation
    if line[0] == "b" and line[1] in APOSTROPHES:
        line = line[2:len( line ) - 1]
    # Remove CRLF
    if line.endswith( '\\n'):
        line = line[:len(line) - 2]
    if line.endswith( '\\r' ):
        line = line[:len( line ) - 2]
    return line


def path_leaf(path):
    """
    Get last leaf in a path. Also remember the head.
    """
    global path_head
    if path and path[-1] in ['/', '\\']:
        path = path[:-1]
    path_head, tail = ntpath.split(path)
    return path_head, tail or ntpath.basename(path_head)


def path_leaf_only(path):
    """
    Get last leaf in a path.
    """
    if not path:
        return EMPTY
    if path.endswith(format_os('/')):
        path = path[:-1]
    head, tail = ntpath.split(path)
    return tail


def remove_color_code(text):
    if '\033' in text:
        text = text.replace( '\033[0m', '' )
        text = text.replace( '\033[31m', '' )
        text = text.replace( '\033[32m', '' )
        text = text.replace( '\033[33m', '' )
        text = text.replace( '\033[34m', '' )
        text = text.replace( '\033[35m', '' )
    return text


def get_coloured_count(count, color=GREEN, zero=RED):
    color = zero if count == 0 else color
    colors = Color.toDict()
    return f'{colors.get(color)}{count}{Color.NC}'


def loop_increment(suffix) -> bool:
    global loop_count, suffix_p
    if suffix != suffix_p:
        suffix_p = suffix
        loop_count = 0
    loop_count += 1
    if loop_count > 100000:
        print( f'{suffix}: Max loop count reached.' )
        return False
    return True


def find_file(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)
    return None


def find_files(name, path):
    paths = []
    for root, dirs, files in os.walk(path):
        if name in files:
            paths.append(os.path.join(root, name))
    return paths


def replace_root_in_path(path, search_string=None, replace_by=''):
    if not search_string:
        slash = format_os( '/' )
        search_string = f'{slash}{APP_NAME}'
    current_path = os.path.dirname( os.path.realpath( __file__ ) )
    index = current_path.find( search_string)
    if current_path.find( search_string) > 0:
        root = current_path[:index]
        if path and path.startswith( root ):
            return path.replace( root, replace_by )
    return path


def sanitize_none(value):
    return None if value == NONE else value


def format_date(date: str, input_date_format=None, output_separator='-') -> str:
    """
    Requirements: Input is formatted string, where year is in yyyy format. Blank can not be a separator (EMPTY can).
    Return: yyyy-mm-dd.
    """
    # Validate before
    if not date or input_date_format not in ('YMD', 'DMY', 'MDY' ):
        return EMPTY
    # If "date time", remove the "time" part
    if len( date ) > 10:
        if ':' in date:
            p = date.find(BLANK)
            if p:
                date = date[:p]
        if len( date ) > 10:
            return EMPTY

    # Get the 2 positions of date separators (like '/' or '-')
    sep_index = [i for i in range(len(date)-1) if date[i] != BLANK and not isInt(date[i])]
    # If no separators, add them
    if not len(sep_index) == 2:
        if sep_index or len( date ) != 8:
            return EMPTY
        if input_date_format == 'YMD':
            return f'{date[:4]}{output_separator}{date[4:6]}{output_separator}{date[6:]}'
        elif input_date_format == 'DMY':
            return f'{date[4:8]}{output_separator}{date[2:4]}{output_separator}{date[:2]}'
        else:  # MDY
            return f'{date[4:8]}{output_separator}{date[:2]}{output_separator}{date[2:4]}'

    # Get uniform date elements
    E1 = date[:sep_index[0]].lstrip()
    E2 = date[sep_index[0]+1:sep_index[1]]
    E3 = date[sep_index[1]+1:].rstrip()

    if input_date_format == 'YMD':
        YY = E1
        MM = _pad_zeroes(E2)
        DD = _pad_zeroes(E3)
    elif input_date_format == 'DMY':
        YY = E3
        MM = _pad_zeroes(E2)
        DD = _pad_zeroes(E1)
    else:  # MDY
        YY = E3
        MM = _pad_zeroes(E1)
        DD = _pad_zeroes(E2)
    # Validate after
    if not len(YY) == 4:
        return EMPTY
    return f'{YY}{output_separator}{MM}{output_separator}{DD}'


def timestamp_from_string(date_Y_m_d, time_H_M_S=None):
    if time_H_M_S:
        time_stamp = time.mktime(
            datetime.datetime.strptime( f'{date_Y_m_d} {time_H_M_S}', '%Y-%m-%d %H:%M:%S' ).timetuple() )
    else:
        time_stamp = time.mktime(
            datetime.datetime.strptime( f'{date_Y_m_d}', '%Y-%m-%d' ).timetuple() )
    return time_stamp


def _pad_zeroes(element, length=2) -> str:
    if len(element) >= length:
        return element
    no_of_zeroes = length - len(element)
    return f'{date_zeroes[:no_of_zeroes]}{element}'


def list_to_string(values: list) -> str:
    if not values:
        return NONE
    # Already a stringed list?
    if is_stringed_list(values):
        return str(values[1:-1])  # Truncate []
    if type( values ) is list or type( values ) is set:
        return ', '.join( values )
    return str(values)


def is_stringed_list(value) -> bool:
    return True if type( value ) is str and len( value ) > 2 and value[0] == '[' and value[-1] == ']' else False


def db_stringed_list_to_list(value) -> []:
    result = []

    if is_stringed_list( value ):
        values = value.strip( '][' ).split( ', ' )
        for v in values:
            for s in DB_LIST_REPRESENTATION_SUBSTITUTE:
                v = v.replace( s, EMPTY )
            result.append( v )
    return result
def get_icon():
    from src.GL.BusinessLayer.SessionManager import Singleton as Session
    icon = f'{Session().images_dir}Logo.png'
    icon = icon if os.path.isfile( icon ) else None
    if not icon:
        return None
    with open(icon, 'rb') as f:
        result = base64.b64encode( f.read() )
    return result
