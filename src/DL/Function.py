from src.DL.Containers.Container import Container
from src.GL.Const import EMPTY


class Function( Container):

    def __init__(self, ID, MO_ID, container_ID, namespace, module_name, parent_type, parent_name, function_name,
                 function_type=EMPTY, line_no_start=0, line_no_end=0, hash=None):
        super().__init__( namespace, module_name, container_type=parent_type, container_name=parent_name,
                          ID=container_ID )
        self._ID = ID
        self._MO_ID = MO_ID
        self._container_ID = container_ID
        self._function_name = function_name
        self._function_type = function_type
        self._line_no_start = line_no_start
        self._line_no_end = line_no_end
        self._hash = hash

    @property
    def ID(self):
        return self._ID

    @property
    def MO_ID(self):
        return self._MO_ID

    @property
    def container_ID(self):
        return self._container_ID

    @property
    def Function_name(self):
        return self._function_name

    @property
    def Line_no_start(self):
        return self._line_no_start

    @property
    def Line_no_end(self):
        return self._line_no_end

    @property
    def Hash(self):
        return self._hash
