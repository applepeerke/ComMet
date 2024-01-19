# ---------------------------------------------------------------------------------------------------------------------
# Function_IO.py
#
# Author      : Peter Heijligers
# Description : Maintain table XRef_Functions.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.BL.Functions import get_names_from_key
from src.DL.CRUD.Container_IO import Container_IO
from src.DL.Function import Function
from src.DL.IOM import IOM
from src.DL.Model import Model, FD, KEY_DELIMITER
from src.DL.DBDriver.Enums import FetchMode
from src.DL.Enums import ContainerType
from src.GL.Const import EMPTY
from src.DL.Table import Table
from src.DL.DBDriver.Att import Att
from src.GL.GeneralException import GeneralException
from src.GL.BusinessLayer.SessionManager import Singleton as Session

PGM = 'Function_IO.py'


model = Model()
container_manager = Container_IO()
iom = IOM()

FU_att_names = Model().get_att_names( Table.Functions )
CL_dict = model.get_att_order_dict( Table.Classes, zero_based=False )
FU_dict = model.get_att_order_dict( Table.Functions, zero_based=False )


class Function_IO( object ):

    def __init__(self):
        self._parms = []

    def add_method(self, function_name, parent_class_name, namespace, module_name, function_type,
                   line_no_start, line_no_end, hash):
        # def ...(p1, p2)
        if not function_name:
            return

        # Write method signature
        parent_class_row = self._get_row(
            Table.Classes,
            where=[
                Att(name=FD.MO_Namespace, value=namespace),
                Att( name=FD.CL_ClassName, value=parent_class_name ),
            ])
        if parent_class_row[0] == 0:
            namespace_name = namespace
            parent_type = ContainerType.Module
            parent_name = module_name
        else:
            namespace_name = parent_class_row[CL_dict[FD.MO_Namespace]]
            parent_type = ContainerType.Class
            parent_name = parent_class_row[CL_dict[FD.CL_ClassName]]

        pk = [
            Att( FD.MO_Namespace, value=namespace_name ),
            Att( FD.MO_ModuleName, value=module_name ),
            Att( FD.CO_ParentName, value=parent_name ),
            Att( FD.FU_FunctionName, value=function_name ),
            ]

        container_id = container_manager.insert(
            namespace, module_name, ContainerType.Function, function_name, function_type, parent_name, parent_type )

        MO = iom.get_obj(
            Table.Modules,
            namespace=namespace,
            module_name=module_name,
        )
        row = []

        for att_name in FU_att_names:
            if att_name == FD.CO_ID:
                row.append( container_id )
            elif att_name == FD.MO_ID:
                row.append( MO.ID )
            elif att_name == FD.MO_Namespace:
                row.append( namespace )
            elif att_name == FD.MO_ModuleName:
                row.append( module_name )
            elif att_name == FD.CO_ContainerName:
                row.append( function_name )
            elif att_name == FD.CO_ContainerType:
                row.append( ContainerType.Function )
            elif att_name == FD.CO_ParentName:
                row.append( parent_name )
            elif att_name == FD.CO_ParentType:
                row.append( parent_type )
            elif att_name == FD.FU_FunctionName:
                row.append( function_name )
            elif att_name == FD.FU_FunctionType:
                row.append( function_type )
            elif att_name == FD.FU_LineNo_start:
                row.append( line_no_start )
            elif att_name == FD.FU_LineNo_end:
                row.append( line_no_end )
            elif att_name == FD.FU_Hash:
                row.append( hash )
            else:
                row.append( EMPTY )

        return Session().db.check_then_insert( Table.Functions, row, where=pk, pgm=PGM )

    @staticmethod
    def _get_row(table_name, where) -> list:
        row = Session().db.fetch(table_name, mode=FetchMode.First, where=where)
        return row if row else [0]

    @staticmethod
    def get_type_from_pk(namespace, module_name, container_name, function_name) -> str:
        row = Session().db.fetch(
            Table.Functions,
            where=[Att(FD.MO_Namespace, value=namespace),
                              Att( FD.MO_ModuleName, value=module_name ),
                              Att( FD.CO_ContainerName, value=container_name ),
                              Att( FD.FU_FunctionName, value=function_name )],
            mode=FetchMode.First)
        if not row:
            raise GeneralException(
                f'{PGM}: Function type not found for key: function={function_name}, container={container_name},'
                f'module={module_name}, namespace={namespace}')
        return row[FU_dict[FD.FU_FunctionType]]

    def get_methods_of_type(self, function_type) -> set:
        methods = Session().db.fetch( Table.Functions )
        return {self._get_logical_key_from_method( m )
                for m in methods if m[FU_dict[FD.FU_FunctionType]] == function_type}

    def key_to_object(self, key) -> Function:
        names = get_names_from_key(key, no_delimiters=4)
        function_name = names[0]
        container_name = names[1]
        container_type = names[2]
        module_name = names[3]
        namespace = names[4]
        FU = iom.get_obj(
            Table.Functions,
            namespace=namespace,
            module_name=module_name,
            container_type=container_type,
            container_name=container_name,
            function_name=function_name
        )
        function_type = self.get_type_from_pk(
            namespace,
            module_name,
            container_name,
            container_type,
            function_name
        )
        return Function(
            ID=FU.ID,
            MO_ID=FU.MO_ID,
            container_ID=FU.Container_ID,
            namespace=namespace,
            module_name=module_name,
            parent_type=container_type,
            parent_name=container_name,
            function_name=function_name,
            function_type=function_type )

    @staticmethod
    def _get_logical_key_from_method(row) -> str:
        return f'{row[FU_dict[FD.FU_FunctionName]]}{KEY_DELIMITER}' \
               f'{row[FU_dict[FD.CO_ContainerType]]}{KEY_DELIMITER}' \
               f'{row[FU_dict[FD.CO_ContainerName]]}{KEY_DELIMITER}' \
               f'{row[FU_dict[FD.MO_ModuleName]]}{KEY_DELIMITER}' \
               f'{row[FU_dict[FD.MO_Namespace]]}'
