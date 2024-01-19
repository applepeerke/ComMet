from src.DL.Enums import ContainerType
from src.GL.Const import EMPTY


class Container(object):
    """
    During parsing just the definition
    """

    def __init__(self,
                 namespace,
                 module_name,
                 container_name=EMPTY,
                 container_type=EMPTY,
                 parent_name=EMPTY,
                 parent_type=EMPTY,
                 function_type=EMPTY,
                 ID=0,
                 ):
        self._ID = ID
        self._namespace = namespace
        self._module_name = module_name
        self._container_name = container_name or module_name
        self._container_type = container_type or ContainerType.Module
        self._parent_name = parent_name
        self._parent_type = parent_type
        self._function_type = function_type

    @property
    def ID(self):
        return self._ID

    @property
    def Namespace(self):
        return self._namespace

    @property
    def Module_name(self):
        return self._module_name

    @property
    def Container_type(self):
        return self._container_type

    @property
    def Container_name(self):
        return self._container_name

    @property
    def Parent_type(self):
        return self._parent_type

    @property
    def Parent_name(self):
        return self._parent_name

    @property
    def Function_type(self):
        return self._function_type

    # Setters

    @ID.setter
    def ID(self, value):
        self._ID = value

    @Container_name.setter
    def Container_name(self, value):
        self._container_name = value
