class Repository(object):

    def __init__(self, ID, dir_name, ):
        self._dir_name = dir_name

    @property
    def Dir_name(self):
        return self._dir_name

