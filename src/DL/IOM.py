# ---------------------------------------------------------------------------------------------------------------------
# IOM.py
#
# Author      : Peter Heijligers
# Description : IO module
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2020-04-09 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.DL.DBDriver.Att import Att
from src.DL.DBDriver.Enums import FetchMode
from src.DL.ORM import row_to_obj
from src.DL.Model import Model, where_atts_to_string, FD

from src.GL.GeneralException import GeneralException
from src.GL.BusinessLayer.SessionManager import Singleton as Session

PGM = 'IOM'
model = Model()


class IOM( object ):

    def __init__(self):
        pass

    @staticmethod
    def get_obj_by_ID(table_name, ID):
        row = Session().db.fetch(table_name, mode=FetchMode.First, where=[Att(FD.ID, value=ID)])
        return row_to_obj( table_name, row) if row else None

    @staticmethod
    def get_obj_by_where(table_name, where, unique=False, required=False):
        rows = Session().db.fetch(table_name, mode=FetchMode.Set, where=where)
        if unique and rows and len( rows ) > 1:
            raise GeneralException( f'{PGM}: "{table_name}" set found but only 1 occurrence expected. Where="{where}"' )
        if required and not rows:
            raise GeneralException( f'{PGM}: "{table_name}" no records found. Where="{where_atts_to_string(where)}"' )
        return row_to_obj( table_name, rows[0]) if rows else None

    def get_obj(self, table_name, unique=True, required=False, **kwargs):
        where = model.get_where(**kwargs)
        return self.get_obj_by_where( table_name, where, unique, required )

