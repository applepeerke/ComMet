# ---------------------------------------------------------------------------------------------------------------------
# Scanner.py
#
# Author      : Peter Heijligers
# Description : Find a string in specified file type in a base directory
#
#
# Date       Ini Description
# ---------- --- ------------------------------------------------------------------------------------------------------
# 2017-08-24 PHe First creation
# ---------------------------------------------------------------------------------------------------------------------

import fnmatch
import os

from src.GL.BusinessLayer.CommentManager import CommentManager
from src.GL.BusinessLayer.FindingsManager import Singleton as Findings_Manager
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.DataLayer.Finding import Finding
from src.GL.BusinessLayer.LogManager import Singleton as Log
from src.GL.Const import MAX_READS_PER_FILE, EMPTY, APP_FIELD_LIMIT, BLANK

PGM = 'Scanner'
CM = CommentManager()
FM = Findings_Manager()


class Scanner(object):

    @property
    def base_dir(self):
        return self._base_dir

    @property
    def file_type(self):
        return self._file_type

    @property
    def include_comment(self):
        return self._include_comment

    @base_dir.setter
    def base_dir(self, value):
        self._base_dir = value

    @file_type.setter
    def file_type(self, value):
        self._file_type = value

    @include_comment.setter
    def include_comment(self, value):
        self._include_comment = value
    """
    Find a string in specified file types in a base directory (specify file_type without ".")
    """
    file_found = 0

    def __init__(self, base_dir=None, file_type=EMPTY):
        self._base_dir = base_dir
        self._file_type = file_type
        self._blacklist = []
        self._path = EMPTY
        self._include_comment = False
        self._session = Session()
        CM.initialize_file( f'.{file_type}' )

    def get_paths(self, file_type=EMPTY, base_dir=EMPTY) -> list:
        scanned_paths = []
        file_type = self._file_type if not file_type else file_type
        base_dir = self._base_dir if not base_dir else base_dir
        for path in self._find_files( f'*.{file_type}', base_dir ):
            """ Scan a source file """
            basename = os.path.basename( path )
            if self._is_valid_file_name(basename):
                scanned_paths.append( path )
        return scanned_paths

    @staticmethod
    def _is_valid_file_name(file_name) -> bool:
        if file_name == '.DS_Store':
            return False
        return True

    def _scan_source(self, path, search_string):
        self._path = path
        self._search_string = search_string
        self._valid_file = True
        self._basename = os.path.basename( path )

        try:
            fo = open( path, 'rb' )
            line = str( fo.readline() )
            self._line_no = 1
            while line != 'b\'\'' and self._line_no < MAX_READS_PER_FILE and self._valid_file:
                self._scan_line( line )
                line = str( fo.readline() )
            fo.close()
        except (IOError, IndexError, Exception) as e:
            text = e.args[1] if e.args and len( e.args ) > 1 else e.args[0]
            file_name, _ = os.path.splitext( self._basename )
            Log().add_line( f'File blacklisted. Error occurred at line no {self._line_no}: "{text}" in {file_name}. '
                            f'Path is "{self._path}"' )
            self._blacklist.append( self._path )

    def _scan_line(self, line ):
        self._line_no += 1
        if not self._is_valid_line( line ):
            return
        index = line.lower().find( self._search_string.lower() )
        if index != -1:
            line, index = self._sophisticate_line( line, index )
            FM.add_finding(
                Finding(
                    path=self._path,
                    line_no=self._line_no,
                    line=line,
                )
            )

    def _is_valid_line(self, line ) -> bool:
        # Not in Comment block
        if not self._include_comment and CM.is_comment( line ):
            return False
        # Skip long lines without spaces (like base64 encoding)
        if len( line ) > 10000 and line.count( " " ) < 2:
            return False
        if self._line_no == MAX_READS_PER_FILE:
            Log().add_line(
                f'Max. reads ({MAX_READS_PER_FILE}) reached in file "{self._basename}"' )
            self._blacklist.append( self._path )
            self._valid_file = False
            return False
        return True

    @staticmethod
    def _sophisticate_line(line, index) -> (str, int):
        # - Replace TAB by BLANK
        if '\\t' in line:
            # Correct index for no. of tabs before index
            for i in range( 0, index ):
                if i + 2 < len( line ) and line[i:i + 2] == '\\t':
                    index -= 1
            line = line.replace( '\\t', BLANK )
        line = line[2:len( line ) - 1]

        # - Now correct find_file position.
        index -= 2 if index >= 2 else 0

        # - Remove CRLF.
        if line.endswith( '\\n' ):
            line = line[:-2]
        if line.endswith( '\\r' ):
            line = line[:-2]

        # - CSV field limit ca. 131000, Excel field limit ca. 32000, 1000 is enough.
        if len( line ) > APP_FIELD_LIMIT:
            if APP_FIELD_LIMIT < index:
                line = f'...{line[index:]}'
            if len( line ) > APP_FIELD_LIMIT:
                line = f'{line[:APP_FIELD_LIMIT]}...'
        return line, index

    @staticmethod
    def _find_files(file_type, basedir=os.curdir):
        """
        Return all file paths matching the specified file type in the specified base directory (recursively).
        """
        for path, dirs, files in os.walk(os.path.abspath(basedir)):
            for filename in fnmatch.filter(files, file_type):
                yield os.path.join(path, filename)
