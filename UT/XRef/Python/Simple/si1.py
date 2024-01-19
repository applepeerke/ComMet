
class Singleton:
    """ Singleton """

    class c0( object ):

        @property
        def P1(self):
            return self._p1

        def __init__(self):
            self._p1 = 0

        def m1(self):
            self._p1 += 1

    # storage for the instance reference
    _instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton._instance is None:
            # Create and remember instance
            Singleton._instance = Singleton.c0()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton_instance'] = Singleton._instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self._instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self._instance, attr, value)
