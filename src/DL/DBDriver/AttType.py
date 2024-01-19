# AttType.py
#
# Author      : Peter Heijligers
# Description : DBDriver attribute
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2018-03-02 PHe Moved from Model


class AttType(object):
    Int = 'INT'
    Float = 'FLOAT'
    Text = 'TEXT'
    Bool = 'BOOL'
    Blob = 'BLOB'
    Id = 'ID'
    Varchar = 'VARCHAR'
    Timestamp = 'TIMESTAMP'
    FieldName = 'FIELDNAME'
    Raw = 'RAW'
    Decimal = 'DECIMAL'

    sanitize_types = [Varchar, Text, Raw]
    numeric_types = [Int, Id, Float, Decimal]
