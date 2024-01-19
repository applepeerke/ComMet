class Message( object):
    def __init__(self, message_code, line, line_no, namespace, module_name):
        self._line_no = line_no
        self._line = line
        self._message_code = message_code
        self._namespace = namespace
        self._module_name = module_name

    @property
    def Message_code(self):
        return self._message_code

    @property
    def Line_no(self):
        return self._line_no

    @property
    def Line(self):
        return self._line

    @property
    def Namespace(self):
        return self._namespace

    @property
    def Module_name(self):
        return self._module_name
