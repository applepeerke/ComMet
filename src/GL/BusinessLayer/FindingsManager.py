# ---------------------------------------------------------------------------------------------------------------------
# FindingsManager.py
#
# Author      : Peter Heijligers
# Description : Consolidate all findings in a cross reference .csv file
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-09-07 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

from src.GL.DataLayer.Finding import Finding


class Singleton:
    """ Singleton """

    class FindingsManager( object ):

        def __init__(self):
            self._findings = []

        def initialize(self):
            self._findings = []

        def add_finding(self, finding: Finding):
            self._findings.append( finding )

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.FindingsManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
