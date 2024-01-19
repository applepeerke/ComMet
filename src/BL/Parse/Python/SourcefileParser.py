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
import builtins
import hashlib
import os
import types

from src.BL.DebugManager import Singleton as DebugManager
from src.BL.Parse.Parser import Parser
from src.BL.Parse.Python.SourcefileWindow_manager import SourcefileWindowManager
from src.BL.Parse.SourcefileParserBase import *
from src.DL.Enums import FunctionType
from src.GL.BusinessLayer.LogManager import Singleton as Log
from src.GL.BusinessLayer.MessageManager import Singleton as MessageManager
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import BLANK, EMPTY
from src.GL.DataLayer.Message import Message
from src.GL.Enums import LogLevel
from src.GL.Functions import path_leaf
from src.GL.GeneralException import GeneralException
from src.GL.Validate import format_os

""" 
Precondition: pos always on 1st position of the item to be processed, or -1
"""

PGM = 'SourcefileParser'
ANNOTATOR_PROPERTY = '@property'
parser = Parser()
message_manager = MessageManager()
slash = format_os( '/' )

builtin_function_names = [name for name, obj in vars( builtins ).items() if
                          isinstance( obj, types.BuiltinFunctionType )]
# from https://www.informit.com/articles/article.aspx?p=453682&seqNum=5
builtin_types = ['int', 'long', 'float', 'complex', 'bool', 'str', 'unicode', 'basestring', 'list', 'tuple', 'xrange',
                 'dict', 'set', 'frozenset', 'types.BuiltinFunctionType', 'types.BuiltinMethodType', 'type', 'object',
                 'types.FunctionType', 'types.InstanceType', 'types.MethodType', 'types.UnboundMethodType',
                 'types.ModuleType', 'file', 'append', 'extend', 'count', 'index', 'insert', 'pop', 'remove',
                 'reverse', 'sort', 'capitalize', 'center', 'decode', 'encode', 'endswith', 'expandtabs', 'find',
                 'isalnum', 'isalpha', 'isdigit', 'islower', 'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower',
                 'lstrip', 'replace', 'rfind', 'rindex', 'rjust', 'rsplit', 'rstrip', 'split', 'splitlines',
                 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zill', 'clear', 'copy', 'has_key',
                 'items', 'iteritems', 'iterkeys', 'itervalues', 'keys', 'update', 'values', 'get', 'setdefault',
                 'popitem', 'difference', 'intersection', 'issubbset', 'issuperset', 'symmetric_difference', 'union',
                 'add', 'difference_update', 'discard', 'intersection_update', 'symmetric_difference_update', ]


class SourcefileParser( SourcefileParserBase ):

    @property
    def error_message(self):
        return self._error_message

    @property
    def warning_messages(self):
        return self._warning_messages

    def __init__(self):
        super().__init__()
        self._session = Session()
        self._this_namespace = None
        self._module_filename = None
        self._module_name = None
        self._prefix = None
        self._function_type = EMPTY
        self._Caller = None
        self._stack = []
        self._stack_index = 0
        self._def_lines = []
        self._def_pos = -1
        self._line_no_start = 0
        self._line_no_end = 0
        self._Def_name = EMPTY

    def parse_file(self, path, base_dir=None) -> bool:
        self._stack = []
        self._stack_index = 0
        self._this_namespace, self._module_filename = path_leaf( path )
        if base_dir:
            this_namespace = f'{self._this_namespace}{format_os( "/" )}'.replace( base_dir, EMPTY )
            self._this_namespace = slash if self._this_namespace and not this_namespace else this_namespace
        self._module_name, file_ext = os.path.splitext( self._module_filename )

        # Validate
        self._prefix = f'{PGM} source file "{self._module_filename}": '
        if file_ext not in supported_file_types:
            self.warning_messages.append(
                f'{self._prefix} error: Extension "{file_ext}" is not supported in path "{path}"' )
            return True

        # Parse
        self._parse_file( path )
        return True if not self.error_message else False

    def _parse_file(self, path):
        """
        :param path: source file path
        """
        # Open file for reading, converting binary to string (utf-8)
        try:
            fo = open( path, 'rb' )
            parser.ini_file( self._this_namespace )
            parser.read_line( fo )

            # Add module.
            self._set_Module_def()

            # Loop until EOF
            while not self.error_message and parser.line != EOF:
                if parser.line and not parser.is_comment:
                    self._ini_line()
                    # Class
                    if self._first_elem == CLASS:
                        self._function_type = FunctionType.Method
                        self._set_Class_def()
                    # Function
                    elif self._first_elem == DEF:
                        self._set_Def_def()
                        # Type=CLASS must be retained but type=PROPERTY reset. (type=FUNCTION is the default).
                        if self._function_type == FunctionType.Property:
                            self._function_type = FunctionType.Method
                if self.error_message:
                    Log().add_line(
                        f'{self._prefix} error at line {parser.line_no}: "{parser.line}"',
                        min_level=LogLevel.Verbose )

                # Next line
                parser.read_line( fo )
            fo.close()
            # Last time (Def is added afterwards)
            self._add_Def_def()
        except IOError as e:
            self._error_message = f'{self._prefix} error: {e.args[1]} at path "{path}"'

    def _ini_line(self):
        # Find 1st element
        self._first_elem = parser.get_next_elem()
        if not self._first_elem or parser.pos == -1:
            return

        # Def mode
        self._first_elem_pos = len(parser.line) - len(parser.line.lstrip())
        if self._def_pos > -1:
            # Level break Def
            if self._first_elem_pos <= self._def_pos:
                self._add_Def_def()
                # Initialize
                self._def_pos = -1
                self._def_lines = []
            else:
                self._def_lines.append( parser.line.replace(BLANK, EMPTY) )

        # Is it a property annotator? (@property or @myAttribute.setter)
        if (self._first_elem == ANNOTATOR_PROPERTY or
                (self._first_elem.startswith( '@' ) and self._first_elem.endswith( '.setter' ))):
            self._Caller.function_type = FunctionType.Property

    def _set_Module_def(self):
        # Initialize Window
        self._Caller = SourcefileWindowManager( self._module_name )

        # Add module
        if module_manager.insert(
                namespace=self._this_namespace,
                filename=self._module_filename,
                module_name=self._module_name
        ) == 0:
            raise GeneralException( f'{__name__}: Module could not be inserted.' )

    def _set_Class_def(self):

        # Example: "...([name_namespace.]name-1, class-type-2):"
        class_name = parser.get_next_elem( delimiters=[BLANK, '(', ':'], LC=False )

        # Set window if a class or method is found.
        self._Caller.new_class( class_name )

        # Write to DB
        if not self._session.db:
            return

        class_manager.insert(
            namespace=self._this_namespace,
            module_name=self._module_name,
            line_no=parser.line_no,
            class_name=class_name,
        )

    def _set_Def_def(self):
        """ Def = Method, property  or function """
        self._def_pos = self._first_elem_pos
        self._def_lines = [parser.line.replace(BLANK, EMPTY)]
        self._line_no_start = parser.line_no

        # def ...(p1, p2)
        self._Def_name = parser.get_next_elem( delimiters=['('], LC=False )
        # Set window if a class or method is found.
        self._Caller.new_def( self._Def_name )

    def _add_Def_def(self):
        """ Add Def afterwards """
        self._line_no_end = parser.line_no
        # noinspection InsecureHash
        hash_obj = hashlib.md5(''.join(self._def_lines).encode())

        # Debug
        if self._session.debug_method_name == self._Def_name:
            DebugManager().add_method_lines(self._this_namespace, self._def_lines)

        method_manager.add_method(
            function_name=self._Def_name,
            parent_class_name=self._Caller.container_name,
            namespace=self._this_namespace,
            module_name=self._module_name,
            function_type=self._get_function_type( self._Def_name ),
            line_no_start=self._line_no_start,
            line_no_end=self._line_no_end,
            hash=hash_obj.hexdigest()
        )

    def _get_function_type(self, function_type) -> str:
        if function_type.startswith( '__' ) and function_type.endswith( '__' ):
            return FunctionType.Internal
        elif not self._function_type:
            return FunctionType.Function
        else:
            return self._function_type

    def _add_message(self, message_code, line_no, line):
        message = Message( message_code, line, line_no, self._this_namespace, self._module_name )
        message_manager.add_message( message )
