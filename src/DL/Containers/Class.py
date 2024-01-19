from src.DL.Containers.Container import Container
from src.DL.Enums import ContainerType


class Class( Container ):

    def __init__(self, ID, container_ID, class_name, module_name, namespace, class_line_no=0):
        super().__init__( namespace, module_name, container_type=ContainerType.Class, container_name=class_name,
                          ID=container_ID )
        self._ID = ID
        self._class_line_no = class_line_no

    @property
    def ID(self):
        return self._ID

    @property
    def Class_line_no(self):
        return self._class_line_no
