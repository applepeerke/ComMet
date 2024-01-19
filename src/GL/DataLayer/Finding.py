# ---------------------------------------------------------------------------------------------------------------------
# Finding.py
#
# Author      : Peter Heijligers
# Description : Validation functions
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2018-10-22 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.GL.Const import EMPTY


class Finding(object):

    @property
    def line_no(self):
        return self._line_no

    @property
    def path(self):
        return self._path

    @property
    def line(self):
        return self._line

    def __init__(self,
                 path=EMPTY,
                 line_no: int = 0,
                 line=EMPTY):
        self._path = path
        self._line_no = line_no
        self._line = line
