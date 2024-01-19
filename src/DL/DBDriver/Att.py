# ---------------------------------------------------------------------------------------------------------------------
# Attribute.py
#
# Author      : Peter Heijligers
# Description : DBDriver attribute
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-09-18 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

import datetime

from .Const import EMPTY, ZERO
from .Enums import Appearance
from .SQLOperator import SQLOperator
from .AttType import AttType

oper = SQLOperator()


def sanitize_value(value, att_type=AttType.Text, max_length=0):
    if not value:
        return value

    max_length_error = 50
    error_message = validate_value( value, att_type )
    if not error_message:
        return value

    # String handling
    if att_type in AttType.sanitize_types:
        # Can length be determined?
        try:
            length = len( value )
        except ValueError:
            max_length = max_length_error if max_length <= 0 else max_length
            length = max_length + 1  # Force max length

        # Check max length
        if 0 < max_length < length:
            try:
                value = (value[:max_length_error] + '..') if length > max_length_error else value
            except (IndexError, ValueError):
                return f'{__name__}.sanitize: Att value "{str( value )}" does not correspond to type "{att_type}".'
    return value


def validate_value(value, att_type, max_length=0) -> str or None:
    valid = True
    if value is None or value == EMPTY:
        return None

    if att_type in AttType.numeric_types:
        if not str( value ).isdigit() \
                and not str(value).replace(',', EMPTY).replace('.', EMPTY).isdigit():
            valid = False

    elif att_type == AttType.Bool:
        try:
            _ = bool( value )
        except ValueError:
            valid = False

    elif att_type == AttType.Timestamp:
        if value != ZERO:
            try:
                datetime.datetime.strptime( value, "%Y-%m-%dT%H:%M:%S.%f" )
            except ValueError:
                valid = False

    # Maximum length
    if max_length > 0:
        if len( value ) > max_length:
            return f'{__name__}.validate_value: Attribute length ({len( value )}) of type {att_type} ' \
                   f'is higher than max ({max_length}). Value="{value}"'

    # Output
    if valid:
        return None
    else:
        if att_type in AttType.sanitize_types:
            value = (value[:50] + '..') if len( value ) > 50 else value
        return f'{__name__}.validate_value: Attribute value "{value}" does not correspond to type "{att_type}".'


def _convert_unknown_2_str(value, max_length=50) -> str:
    try:
        value = (value[:max_length] + '..')
        return value
    except ValueError:
        return f'{__name__}: ERROR: a value of unknown type could not be converted to string.'


class Att( object ):

    def __init__(
            self, name, value=EMPTY, type=AttType.Varchar, length=0, description=EMPTY, default=None, seqno=0,
            desc_short=None, colhdg_report=None, colhdg_db=None, derived=False, relation=oper.EQ, origin=None,
            arg_name=None, appearance=Appearance.Label, col_width=0, visible=True, optional=False):
        """

        :param name: Name
        :param value: Value
        :param type: Type
        :param length: Length
        :param description: Description (defaults to name.title())
        :param default: Default value (if not set, will be set to default type)

        :param seqno: Seq. no. in a report
        :param desc_short: Short description in a report
        :param colhdg_report: Column heading in a report (defaults to name)

        :param colhdg_db: Db column heading (defaults to name)
        :param derived: Db derived
        :param relation: Db relation
        :param origin: Db origin
        :param arg_name: Parameter name
        :param appearance: GUI (sg) Appearance
        :param col_width: GUI table column width
        :param visible: GUI visible
        :param optional: Optional in e.g. csv to import in database
        """
        self._name = name
        self._value = value
        self._type = type
        self._length = length
        self._description = name.title() if description == EMPTY else description
        self._seqno = seqno
        self._colhdg_report = colhdg_report if colhdg_report else name
        self._colhdg_db = colhdg_db if colhdg_db else name
        self._derived = derived
        self._relation = relation
        self._origin = origin
        self._title_short = desc_short
        self._arg_name = arg_name
        self._appearance = appearance
        self._col_width = col_width
        self._visible = visible
        self._optional = optional

        # Set the default
        if default is None:
            if type in AttType.sanitize_types:
                self._default = EMPTY
            elif type == AttType.Timestamp:
                self._default = datetime.date.min
            elif type in AttType.numeric_types:
                self._default = 0
            elif type == AttType.Bool:
                self._default = False
            else:
                self._default = None

        self.set_relation()

    def set_relation(self, relation=None):
        # Set relation LIKE
        if isinstance(self._value, str) and self._value and len(self._value) > 1 \
                and (self._value.startswith('%') or self._value.endswith('%')):
            self._relation = oper.LIKE
            return
        elif relation:
            self._relation = relation

    """
    Getters
    """

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    @property
    def length(self):
        return self._length

    @property
    def description(self):
        return self._description

    @property
    def default(self):
        return self._default

    @property
    def desc_short(self):
        return self._title_short

    @property
    def colhdg_report(self):
        return self._colhdg_report

    @property
    def colhdg_db(self):
        return self._colhdg_db

    @property
    def derived(self):
        return self._derived

    @property
    def relation(self):
        return self._relation

    @property
    def col_width(self):
        return self._col_width

    @property
    def arg_name(self):
        return self._arg_name

    @property
    def seqno(self):
        return self._seqno

    @property
    def origin(self):
        return self._origin

    @property
    def appearance(self):
        return self._appearance

    @property
    def visible(self):
        return self._visible

    @property
    def optional(self):
        return self._optional

    """
    Setters
    """

    @value.setter
    def value(self, value):
        self._value = value

    @desc_short.setter
    def desc_short(self, val):
        self._title_short = val

    @appearance.setter
    def appearance(self, value):
        self._appearance = value

    @visible.setter
    def visible(self, value):
        self._visible = value

    @description.setter
    def description(self, value):
        self._description = value

    @colhdg_report.setter
    def colhdg_report(self, value):
        self._colhdg_report = value
