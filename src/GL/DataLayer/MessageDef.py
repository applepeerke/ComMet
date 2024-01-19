class MessageDef( object ):

    @property
    def Code(self):
        return self._code

    @property
    def Severity(self):
        return self._severity

    def __init__(self, code, severity):
        self._code = code
        self._severity = severity

