from src.DL.Enums import ContainerType, FunctionType
from src.GL.Const import EMPTY


class SourcefileWindowManager( object ):
    """
    Sourcefile can contain classes ("class") and functions ("def").
                        class   def parent_class function_type
    class c1()          c1      ""  ""
        class   c2()    c2      ""  c1
            def d1()    c2      d1  c1           PROPERTY
            def d2()    c2      d2  c1           METHOD
        def d3()        c1      d3  ""           FUNCTION
    def d4()            ""      d4  ""           FUNCTION
    """

    @property
    def container_name(self):
        return self._class_name

    @property
    def container_type(self):
        return self._container_type

    @property
    def parent_container_name(self):
        return self._parent_container_name

    @property
    def parent_container_type(self):
        return self._parent_container_type

    @property
    def function_name(self):
        return self._function_name

    @property
    def function_type(self):
        return self._function_type

    @property
    def function_parm_names(self):
        return self._function_parm_names

    # Setters
    @function_type.setter
    def function_type(self, value):
        self._function_type = value

    def __init__(self, container_name):
        self._class_name = container_name
        self._container_type = ContainerType.Module
        self._parent_container_position = 0
        self._parent_container_name = container_name
        self._parent_container_type = ContainerType.Module
        self._function_name = EMPTY
        self._function_type = EMPTY
        self._function_parm_names = []

        self._class_line_position = 0
        self._first_elem_pos = 0
        self._last_class_or_function_position = 0
        self._class_stack = []
        # Initially the parent is the module
        self._parent_class_stack = [
            [self._parent_container_name,
             self._parent_container_type,
             0]]

    def new_class(self, name):
        self._container_type = ContainerType.Class
        # Nested Class: Remember as parent class.
        self._push_parent_class()
        # End class.
        if self._first_elem_pos <= self._class_line_position:
            self._pop_class()
        # Add new class to stack.
        self._push_class( name )
        # Init function
        self._function_name = EMPTY
        self._function_type = EMPTY
        self._function_parm_names = []
        self._new_exit()

    def new_def(self, name ):
        self._function_type = FunctionType.Function if self._container_type == ContainerType.Module \
            else FunctionType.Method
        # Previous class ended?
        if self._first_elem_pos <= self._class_line_position:
            self._pop_class()
        self._function_name = name
        self._new_exit()

    def _new_exit(self):
        # De-indentation: reset def type (PROPERTY, METHOD, FUNCTION)
        if self._first_elem_pos <= self._last_class_or_function_position:
            self._function_type = EMPTY
        # Remember "class" or "def" position
        self._last_class_or_function_position = self._first_elem_pos

    def _push_class(self, class_name ):
        self._class_stack.append([class_name, self._first_elem_pos])
        # Set class
        self._class_name = class_name
        self._class_line_position = self._first_elem_pos

    def _pop_class(self):
        if not self._class_stack:
            return
        elem = self._class_stack.pop(len(self._class_stack)-1)
        self._class_name = elem[0]
        self._class_line_position = elem[1]
        # Pop parent class too
        self._pop_parent_class()

    def _push_parent_class(self):
        if self._first_elem_pos > self._class_line_position:
            self._parent_class_stack.append([self._class_name, self._class_line_position])

    def _pop_parent_class(self):
        if self._class_line_position <= self._parent_container_position:
            if self._parent_class_stack:
                elem = self._parent_class_stack.pop( len( self._parent_class_stack ) - 1 )
                self._parent_container_name = elem[0]
                self._parent_container_position = elem[2]
            else:
                self._parent_container_name = EMPTY
                self._parent_container_position = 0
