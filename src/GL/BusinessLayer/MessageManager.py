# ---------------------------------------------------------------------------------------------------------------------
# MessageManager.py
#
# Author      : Peter Heijligers
# Description : Maintain Messages
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2021-09-09 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------
from src.GL.DataLayer.Message import Message


class Singleton:
    """ Singleton """

    class MessageManager( object ):

        @property
        def Expected_message_codes(self):
            return self._expected_message_codes

        @property
        def Messages(self):
            return self._messages

        def __init__(self, expected_message_codes=None):
            self._expected_message_codes = expected_message_codes
            self._messages = {}

        def add_message(self, message: Message):
            key = message.Message_code
            if not self._messages.get(key):
                self._messages[key] = []
            # Unique messages
            if not any(M.Line == message.Line for M in self._messages[key]):
                self._messages[key].append( message )

    # storage for the instance reference
    _instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton._instance is None:
            # Create and remember instance
            Singleton._instance = Singleton.MessageManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton_instance'] = Singleton._instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self._instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self._instance, attr, value)
