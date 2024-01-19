# ---------------------------------------------------------------------------------------------------------------------
# Class_manager.py
#
# Author      : Peter Heijligers
# Description : Maintain table XRef_Classes.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.BL.Parse.SourcefileParserBase import IOM
from src.DL.CRUD.Container_IO import Container_IO
from src.DL.Model import FD, Model
from src.DL.Enums import ContainerType
from src.GL.Const import EMPTY
from src.DL.Table import Table
from src.DL.DBDriver.Att import Att
from src.GL.BusinessLayer.SessionManager import Singleton as Session

PGM = 'Class_manager.py'
TABLE = Table.Classes

att_names = Model().get_att_names( Table.Classes )
CL_dict = Model().get_att_order_dict( Table.Classes, zero_based=False )
FU_dict = Model().get_att_order_dict( Table.Functions, zero_based=False )

iom = IOM()
container_manager = Container_IO()


class Class_IO( object ):

    def __init__(self):
        pass

    def insert(self, namespace, module_name, line_no, class_name) -> int:
        pk = self._get_pk( namespace, module_name, class_name )
        container_ID = container_manager.insert( namespace, module_name, ContainerType.Class, class_name )
        row = []
        for att_name in att_names:
            if att_name == FD.CO_ID:
                row.append(container_ID)
            elif att_name == FD.MO_Namespace:
                row.append(namespace) if namespace else row.append(EMPTY)
            elif att_name == FD.CL_ClassName:
                row.append(class_name) if class_name else row.append(EMPTY)
            elif att_name == FD.MO_ModuleName:
                row.append(module_name) if module_name else row.append(EMPTY)
            elif att_name == FD.CL_LineNo:
                row.append( line_no )
            else:
                row.append(EMPTY)

        return Session().db.check_then_insert( TABLE, row, where=pk, pgm=PGM )

    @staticmethod
    def _get_pk(namespace, module_name, class_name) -> list:
        return [
            Att( FD.MO_Namespace, value=namespace ),  # pk-1
            Att( FD.MO_ModuleName, value=module_name ),  # pk-2
            Att( FD.CL_ClassName, value=class_name ) ]  # pk-3
