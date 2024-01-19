# ---------------------------------------------------------------------------------------------------------------------
# SourcefileParser.py
#
# Author      : Peter Heijligers
# Description : Build a call x-ref from a source file.
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
import abc

from src.DL.IOM import IOM
from src.DL.CRUD.Module_IO import Module_IO
from src.DL.CRUD.Function_IO import Function_IO
from src.DL.CRUD.Class_IO import Class_IO
from src.DL.Model import Model
from src.DL.Table import Table

EOF = 'b\'\''
CRLF = '\\r\\n'
IMPORT = 'import'
FROM = 'from'
DEF = 'def'
CLASS = 'class'
SRCFILE = '*Module'

ACTORS_IGNORE = ['__init__']

supported_file_types = ['.py']
CL_dict = Model().get_att_order_dict( Table.Classes, zero_based=False )

module_manager = Module_IO()
method_manager = Function_IO()
class_manager = Class_IO()
IOM = IOM()
""" 
Precondition: pos always on 1st position of the item to be processed, or -1
"""


class SourcefileParserBase( metaclass=abc.ABCMeta ):

    @property
    @abc.abstractmethod
    def error_message(self):
        pass

    @property
    @abc.abstractmethod
    def warning_messages(self):
        pass

    def __init__(self):
        self._module_filename = None
        self._this_class_name = None
        self._stack_class = None
        self._function_name = None
        self._this_namespace = None
        self._current_class_name = None
        self._error_message = None
        self._warning_messages = []
        self._prefix = None
        self._local_class_names = {}

    @abc.abstractmethod
    def parse_file(self, path, base_dir):
        pass

    @abc.abstractmethod
    def _set_Module_def(self):
        pass

    @abc.abstractmethod
    def _set_Class_def(self):
        pass

    @abc.abstractmethod
    def _set_Def_def(self):
        pass
