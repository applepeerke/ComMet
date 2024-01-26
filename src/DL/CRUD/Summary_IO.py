# ---------------------------------------------------------------------------------------------------------------------
# Summary_IO.py
#
# Author      : Peter Heijligers
# Description : Maintain table Summary.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2024-01-26 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.DL.DBDriver.Att import Att
from src.DL.Model import FD
from src.DL.Table import Table
from src.GL.BusinessLayer.SessionManager import Singleton as Session

PGM = 'Summary_IO.py'


class Summary_IO(object):

    @staticmethod
    def insert(function_name, count=0, max_equal=0):
        if not function_name:
            return

        row = [function_name, count, max_equal]
        return Session().db.check_then_insert(
            Table.Summary, row, where=[Att(FD.FU_FunctionName, function_name)], pgm=PGM)
