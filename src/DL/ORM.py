from src.DL.Containers.Container import Container
from src.DL.Function import Function
from src.DL.Containers.Module import Module
from src.DL.Model import Model, FD
from src.DL.Table import Table
from src.DL.Containers.Class import Class
from src.DL.Repository import Repository
from src.GL.GeneralException import GeneralException

RP_dict = Model().get_att_order_dict( Table.Repositories, zero_based=False )
CO_dict = Model().get_att_order_dict( Table.Containers, zero_based=False )
MO_dict = Model().get_att_order_dict( Table.Modules, zero_based=False )
CL_dict = Model().get_att_order_dict( Table.Classes, zero_based=False )
FU_dict = Model().get_att_order_dict( Table.Functions, zero_based=False )


def repository_obj(row):
    obj = Repository(
        dir_name=row[RP_dict[FD.RP_Dir_name]],
        ID=row[0]
    )
    return obj


def container_obj(row):
    obj = Container(
        namespace=row[CO_dict[FD.MO_Namespace]],
        module_name=row[CO_dict[FD.MO_ModuleName]],
        container_type=row[CO_dict[FD.CO_ContainerType]],
        container_name=row[CO_dict[FD.CO_ContainerName]],
        ID=row[0]
    )
    return obj


def class_obj(row):
    obj = Class(
        ID=row[0],
        container_ID=row[CL_dict[FD.CO_ID]],
        namespace=row[CL_dict[FD.MO_Namespace]],
        module_name=row[CL_dict[FD.MO_ModuleName]],
        class_name=row[CL_dict[FD.CL_ClassName]],
        class_line_no=row[CL_dict[FD.CL_LineNo]],
    )
    return obj


def function_obj(row):
    obj = Function(
        ID=row[0],
        MO_ID=row[FU_dict[FD.MO_ID]],
        container_ID=row[FU_dict[FD.CO_ID]],
        namespace=row[FU_dict[FD.MO_Namespace]],  # Redundant
        module_name=row[FU_dict[FD.MO_ModuleName]],  # Redundant
        parent_type=row[FU_dict[FD.CO_ParentType]],
        parent_name=row[FU_dict[FD.CO_ParentName]],
        function_name=row[FU_dict[FD.FU_FunctionName]],
        function_type=row[FU_dict[FD.FU_FunctionType]],
        line_no_start=row[FU_dict[FD.FU_LineNo_start]],
        line_no_end=row[FU_dict[FD.FU_LineNo_end]],
        hash=row[FU_dict[FD.FU_Hash]]
    )
    return obj


def module_obj(row):
    obj = Module(
        ID=row[0],
        namespace=row[MO_dict[FD.MO_Namespace]],
        filename=row[MO_dict[FD.MO_Filename]],
    )
    return obj


def row_to_obj(table_name, row):
    if table_name == Table.Repositories:
        return repository_obj( row )
    if table_name == Table.Containers:
        return container_obj( row )
    if table_name == Table.Modules:
        return module_obj( row )
    elif table_name == Table.Classes:
        return class_obj( row )
    elif table_name == Table.Functions:
        return function_obj( row )
    else:
        raise GeneralException(f'{__name__}: table name "{table_name}" is not implemented.')
