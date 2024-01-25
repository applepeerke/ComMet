import unittest
import os
import fnmatch


def find_UT_files(basedir=os.curdir):
    """
    Return all file paths matching the specified file type in the specified base directory (recursively).
    """
    for path, dirs, files in os.walk(os.path.abspath( basedir)):
        for filename in fnmatch.filter(files, '*.py'):
            if filename.startswith('UT_Core') and filename != 'UT_Core_000_All.py':
                name, ext = os.path.splitext(filename)
                yield name


suite = unittest.TestSuite()

unit_tests = []
for t in find_UT_files():
    unit_tests.append(t)
unit_tests.sort()

for t in unit_tests:
    try:
        # If the module defines a suite() get_index, call it to get the suite.
        mod = __import__(t, globals(), locals(), ['suite'])
        suitefn = getattr(mod, 'suite')
        suite.addTest(suitefn())
    except (ImportError, AttributeError):
        # else, just load all the test cases from the module.
        suite.addTest(unittest.defaultTestLoader.loadTestsFromName(t))

unittest.TextTestRunner().run(suite)
