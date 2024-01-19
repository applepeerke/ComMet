# ---------------------------------------------------------------------------------------------------------------------
# Module_manager.py
#
# Author      : Peter Heijligers
# Description : Maintain table Containers
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2011-09-06 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.DL.Containers.Container import Container
from src.DL.IOM import IOM
from src.DL.DBDriver.Att import Att
from src.DL.Table import Table
from src.DL.Model import FD, Model
from src.DL.Enums import ContainerType
from src.GL.Const import EMPTY
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.GeneralException import GeneralException

PGM = 'Container_manager.py'
TABLE = Table.Containers
att_names = Model().get_att_names( TABLE )
iom = IOM()


class Container_IO( object ):

    def __init__(self):
        pass

    @staticmethod
    def insert(namespace, module_name, container_type, container_name=EMPTY, parent_name=EMPTY, parent_type=EMPTY,
               function_type=EMPTY) -> int or None:

        pk = [
            Att( FD.MO_Namespace, value=namespace ),
            Att( FD.MO_ModuleName, value=module_name ),
            Att( FD.CO_ContainerType, value=container_type ),
            Att( FD.CO_ContainerName, value=container_name ),
            Att( FD.CO_ParentName, value=parent_name ),
            Att( FD.CO_ParentType, value=parent_type ),
            ]

        row = []
        for att_name in att_names:
            if att_name == FD.MO_Namespace:
                row.append(namespace) or EMPTY
            elif att_name == FD.MO_ModuleName:
                row.append( module_name ) or EMPTY
            elif att_name == FD.CO_ContainerType:
                row.append(container_type) or EMPTY
            elif att_name == FD.CO_ContainerName:
                row.append( container_name ) or EMPTY
            elif att_name == FD.CO_ParentName:
                row.append( parent_name ) or EMPTY
            elif att_name == FD.CO_ParentType:
                row.append( parent_type ) or EMPTY
            elif att_name == FD.FU_FunctionType:
                row.append( function_type ) or EMPTY
            else:
                row.append(EMPTY)

        return Session().db.check_then_insert( TABLE, row, where=pk, pgm=PGM )

    @staticmethod
    def fetch_obj(
            namespace, module_name, container_type, container_name, parent_name=EMPTY, parent_type=EMPTY) -> Container:
        # If container type is a function, then it is in fact a Module.
        if container_type == ContainerType.Function:
            container_type = ContainerType.Module
        # Base object
        CO = Container(
            namespace=namespace, module_name=module_name, container_type=container_type, container_name=container_name,
            parent_name=parent_name, parent_type=parent_type )

        if container_type == ContainerType.Unknown:
            return CO
        # Populate the ID from database
        elif container_type == ContainerType.Module:
            MO = iom.get_obj(
                Table.Modules, namespace=namespace, module_name=module_name )
            CO.ID = MO.ID if MO else 0
        elif container_type == ContainerType.Class:
            CL = iom.get_obj(
                Table.Classes, namespace=namespace, module_name=module_name, class_name=container_name )
            CO.ID = CL.ID if CL else 0
        else:
            raise GeneralException(f'{PGM}.fetch_obj: unsupported container type "{container_type}"')
        return CO
