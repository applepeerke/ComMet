import os

from src.DL.Containers.Container import Container


class Module(Container):

    def __init__(self, ID, namespace, filename, ):
        super().__init__( namespace, filename, ID=ID  )
        self._namespace = namespace
        self._filename = filename
        self._module_name, ext = os.path.splitext(self._filename)

    @property
    def Filename(self):
        return self._filename

