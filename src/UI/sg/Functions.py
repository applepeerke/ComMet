from src.GL.Const import EMPTY, BLANK
from src.GL.Result import Result
from src.UI.sg.Const import STATUS_MESSAGE, STATUSBAR_WIDTH
from src.UI.sg.Constants.Color import STATUSBAR_COLOR_INFO, STATUSBAR_COLOR_BACKGROUND
from src.UI.sg.ViewModels.MessageBox import message_box

gui_name_types = {}
gui_values = {}


def get_name_from_key(k, ignore_types: list = None) -> str:
    """ Example: 'CHECK_ONLY_CB:' -> 'CHECK_ONLY' """
    if isinstance(k, tuple):  # Table row
        return k[0]
    # Special case: Calendar widget is empty, date is in WTyp.IN, not in WTyp.CA.
    # In that case return the whole key.
    if ignore_types:
        for i in ignore_types:
            if k and k.endswith( i ):
                return k
    p = k.rfind( '_' ) if k else -1
    return k[:p] if p > 0 else EMPTY


def get_name_from_text(text, LC=False) -> str:
    """ Example: 'Check only: ' -> 'CHECK_ONLY' """
    if not text or not isinstance( text, str ):
        return text
    text = text.replace( BLANK, '_' ).replace( ':', EMPTY )
    if text and text[0] == '_':
        text = text[1:]
    if text and text[-1] == '_':
        text = text[:-1]
    if not text:
        return EMPTY
    return text.lower() if LC else text.upper()


def get_col_widths(data, col_widths=None, col_width_max=80) -> dict:
    """
    data: header with details
    col_widths: {No : col_width } or None. Default col_width=0. No. is 0-based.
    """
    col_widths = {} if not col_widths else col_widths
    if not data or len( data ) <= 1:  # No details
        return col_widths

    # Determine maximum col_widths encountered (with a maximum of max_col_width).
    col_widths_result = {}
    for row in data:  # Every data row
        for i in range( len( row ) ):  # Every row attribute
            # Static col_width if specified as > 0.
            col_w = col_widths.get( i )
            if col_w and col_w > 0:
                col_widths_result[i] = col_w
            # Dynamic col_width if it is not specified.
            elif isinstance( row[i], str ):
                max_w = col_widths_result.get( i ) or 0
                col_widths_result[i] = max( min( col_width_max, len( row[i] ) ), max_w )
    return col_widths_result


def status_message(window, result: Result = None):
    if result:
        if result.messages or len(result.text) > STATUSBAR_WIDTH:
            text = result.get_messages_as_message() if result.messages else result.text
            message_box( text, severity=result.severity )
        else:
            window[STATUS_MESSAGE].update(
                result.text, text_color=STATUSBAR_COLOR_INFO, background_color=STATUSBAR_COLOR_BACKGROUND )
    else:
        window[STATUS_MESSAGE].update(EMPTY)


def confirmed(result: Result) -> bool:
    """
    Is question confirmed?
    N.B. Return False if not OK and no "?".
    """
    box_result = result.get_messages_as_message()
    cont_text = result.text \
        if (result.text.endswith('?') and not result.ER)\
        else EMPTY
    return False if not cont_text and not result.OK \
        else message_box(box_result, severity=result.severity, cont_text=cont_text)
