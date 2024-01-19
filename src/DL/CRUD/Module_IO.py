# ---------------------------------------------------------------------------------------------------------------------
# Module_manager.py
#
# Author      : Peter Heijligers
# Description : Maintain table XRef_Classes.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.DL.CRUD.Container_IO import Container_IO
from src.DL.DBDriver.Att import Att
from src.DL.Table import Table
from src.DL.Model import FD, Model
from src.DL.Enums import ContainerType
from src.GL.Const import EMPTY
from src.GL.BusinessLayer.SessionManager import Singleton as Session

PGM = 'Module_manager.py'
TABLE = Table.Modules
att_names = Model().get_att_names( TABLE )

container_manager = Container_IO()


class Module_IO( object ):

    def __init__(self):
        pass

    @staticmethod
    def insert(namespace, filename, module_name) -> int or None:

        pk = [
            Att( FD.MO_ModuleName, value=filename ),
            Att( FD.MO_Namespace, value=namespace ),
            ]
        container_ID = container_manager.insert( namespace, module_name, ContainerType.Module )
        row = []

        for att_name in att_names:
            if att_name == FD.CO_ID:
                row.append(container_ID)
            if att_name == FD.MO_Namespace:
                row.append(namespace) or EMPTY
            elif att_name == FD.MO_Filename:
                row.append( filename ) or EMPTY
            elif att_name == FD.MO_ModuleName:
                row.append(module_name) or EMPTY
            else:
                row.append(EMPTY)

        return Session().db.check_then_insert( TABLE, row, where=pk, pgm=PGM )
