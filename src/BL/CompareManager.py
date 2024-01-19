import os

from src.BL.Parse.Python.SourcefileParser import SourcefileParser
from src.DL.CRUD.Repository_IO import Repository_IO
from src.DL.DBDriver.Att import Att
from src.DL.DBDriver.Enums import FetchMode
from src.DL.DBDriver import DBDriver
from src.DL.Model import FD, Model
from src.DL.Table import Table
from src.DL.Enums import FunctionType
from src.GL.BusinessLayer.CsvManager import CsvManager
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.BusinessLayer.ConfigManager import Singleton as ConfigManager, CF_LIST_DIFF_ONLY, CF_REPO_DIRS, CF_FILE_NAME
from src.GL.BusinessLayer.Scanner import Scanner
from src.DL.ORM import row_to_obj
from src.GL.Const import EMPTY, TRUE
from src.GL.Enums import ResultCode, MessageSeverity
from src.GL.GeneralException import GeneralException
from src.GL.Result import Result
from src.DL.IOM import IOM

model = Model()
session = Session()
csvm = CsvManager()
CM = ConfigManager()
scanner = Scanner()

repository_IO = Repository_IO()
iom = IOM()


def _get_common_leading_part_size(paths) -> int:
    if len( paths ) < 2:
        return 0

    # Look for leading part which must be equal in all paths.
    leading = 0
    ref_path = list( paths )[0]
    for n in range( len( ref_path ) ):
        for path in list( paths ):
            if path[:n] != ref_path[:n]:
                return n - 1
    return leading


def _get_sophisticated_paths(paths) -> list:
    common_leading_part_size = _get_common_leading_part_size( paths )
    # A. Do not truncate the paths
    if common_leading_part_size == 0:
        return [path for path in paths]
    # B. Truncate the paths
    else:
        prefix = '..' if common_leading_part_size > 0 else EMPTY
        return [f'{prefix}{path[common_leading_part_size - 1:]}' for path in paths]


class CompareManager( object ):

    @property
    def repo_dirs(self):
        return self._repo_dirs

    @property
    def repo_dirs_sophisticated(self):
        return self._repo_dirs_sophisticated

    @property
    def valid_repo_paths(self):
        return self._valid_repo_paths

    def __init__(self):
        # Repo paths
        self._repo_dirs = CM.get_config_item( CF_REPO_DIRS ) or []
        self._repo_dirs_sophisticated = _get_sophisticated_paths( self._repo_dirs )
        # Compare paths
        # self._compare_paths = db_stringed_list_to_list(CM.get_config_item(CF_INPUT_PATHS))
        # self._compare_paths_sophisticated = _get_sophisticated_paths(self._compare_paths)
        self._db: DBDriver = Session().db
        self._path_methods = {}
        self._out_rows = []
        self._result = Result()
        self._valid_repo_paths = set()
        self._error_messages = []

    def _validate_path(self, base_dir) -> bool:
        """
        N.B. Only 1 path should occur.
        """
        file_name = CM.get_config_item( CF_FILE_NAME )
        paths = scanner.get_paths( file_type='py', base_dir=base_dir )
        found_paths = [p for p in paths if p.endswith( file_name )]
        count = len( found_paths )
        if count == 1:
            self._valid_repo_paths.add( found_paths[0] )
            return True

        error_text = (
            f'File name {file_name} does not exist in repository "{base_dir}".'
            if count == 0 else
            f'{count} file names {file_name} found, only 1 is allowed. Repository is "{base_dir}".' )

        self._error_messages.append(error_text)
        return False

    """
    CRUD on repo dirs in MEMORY
    """

    def add_repo_dir(self, dir_name) -> Result:
        if not dir_name:
            return Result( ResultCode.Error, text='Dir name is required.' )
        if dir_name not in self._repo_dirs:
            if not self._validate_path( dir_name ):
                return Result(ResultCode.Error, messages=self._error_messages)

            self._repo_dirs.append( dir_name )
            self._sophisticate_repo_dirs( self._repo_dirs )
            return Result( text='Dir name is valid and has been added.' )
        else:
            return Result( ResultCode.Error, text='Dir name already exists.' )

    def remove_repo_dir(self, dir_name) -> Result:
        if not dir_name:
            return Result( ResultCode.Error, text='Dir name is required.' )
        if dir_name in self._repo_dirs:
            self._repo_dirs.remove( dir_name )
            self._sophisticate_repo_dirs( self._repo_dirs )
            return Result( text='Dir name has been removed.' )
        else:
            return Result( ResultCode.Error, text='Dir name does not exist in the list.' )

    def clear_repo_dirs(self) -> Result:
        self._repo_dirs = []
        self._sophisticate_repo_dirs( self._repo_dirs )
        return Result( text='List has been cleared.' )

    def _sophisticate_repo_dirs(self, dirs):
        self._repo_dirs_sophisticated = _get_sophisticated_paths( dirs )
        CM.set_config_item( CF_REPO_DIRS, dirs )

    def get_dir_from_soph(self, path_soph) -> str:
        for p in self._repo_dirs:
            if p.endswith( path_soph.lstrip( '..' ) ):
                return p

    """
    CRUD on compare paths in MEMORY
    """

    # def add_compare_path(self, path) -> Result:
    #     if not path:
    #         return Result( ResultCode.Error, text='Path is required.' )
    #     if path not in self._compare_paths:
    #         self._compare_paths.append( path )
    #         self._sophisticate_compare_paths(self._compare_paths)
    #         return Result( text='Path has been added.' )
    #     else:
    #         return Result( ResultCode.Error, text='Path already exists in the list.' )
    #
    # def remove_compare_path(self, path) -> Result:
    #     if not path:
    #         return Result( ResultCode.Error, text='Path is required.' )
    #     if path in self._compare_paths:
    #         self._compare_paths.remove( path )
    #         self._sophisticate_compare_paths(self._compare_paths)
    #         return Result( text='Path has been removed.' )
    #     else:
    #         return Result( ResultCode.Error, text='Path does not exist in the list.' )
    #
    # def clear_compare_paths(self) -> Result:
    #     self._compare_paths = []
    #     self._sophisticate_compare_paths( self._compare_paths )
    #     return Result( text='List has been cleared.' )
    #
    # def _sophisticate_compare_paths(self, paths):
    #     self._compare_paths_sophisticated = _get_sophisticated_paths( paths )
    #     CM.set_setting( CF_INPUT_PATHS, paths )

    # def get_path_from_soph(self, path_soph) -> str:
    #     for p in self.compare_paths:
    #         if p.endswith(path_soph.lstrip('..')):
    #             return p

    def compare(self) -> Result:
        """
        Example output:
        | ------------- | ----------| ------------------------|-----------------------|
        | Method name   | All equal | ../CxMon/DBDriver.py    | ../CRiSp/DBDriver.py  |
        | ------------- | ----------| ------------------------|-----------------------|
        | insert        |   N       | 3123gghe7rweywie        | hgssfd87rwefs8dufs    |
        | update        |   N       | hdidmdisd3u8sd          | kfsydsr9erywernw      |
        | ------------- | ----------| ------------------------|-----------------------|
        """
        self._error_messages = []
        file_parser = SourcefileParser()
        # valid_repo_paths is cleared after exiting the program, while repo_dirs are saved in config.
        [self._validate_path( d ) for d in self._repo_dirs]
        if self._error_messages:
            return Result( ResultCode.Error, messages=self._error_messages )

        # Clear DB
        [session.db.clear( t ) for t in model.DB_tables]

        # Create DB - Parse paths (every compare file)
        [self._insert_repository( d ) for d in self._repo_dirs]
        [file_parser.parse_file( p ) for p in self._valid_repo_paths]

        # For every compare path (module), list the Method objects.
        [self._list_methods( module_ID ) for module_ID in
         [row[0] for row in self._db.fetch( Table.Modules, mode=FetchMode.WholeTable )]]

        # A. List all method_names
        method_names = {
            F.Function_name for Functions in self._path_methods.values()
            for F in Functions if F.Function_type in (FunctionType.Method, FunctionType.Function)
        }

        if not method_names:
            return Result(
                ResultCode.Error, f'No method names found in the {len( self._repo_dirs )} specified repositories.' )

        # B. Assign number of occurrences to the method_names
        # Example: { 1: [m1, m2], 2: [m4], 3: [m3]. 4: [] }.
        # Method_name m1 and m2 occur 1 time in all paths, m4 2 times and m3 3 times.
        method_name_occurrences = {}
        count_max = 0
        for method_name in method_names:
            count = 0
            for Methods in self._path_methods.values():
                for M in Methods:
                    if M.Function_name == method_name:
                        count += 1
                        count_max = count if count > count_max else count_max
                        break
            if count not in method_name_occurrences:
                method_name_occurrences[count] = [method_name]
            else:
                method_name_occurrences[count].append( method_name )

        # C. Output: List methods per number of occurrences (desc)
        self._out_rows = []
        # Header
        header_row = ['method name', 'Count', 'Max equal']
        header_row.extend( [self._get_repo_dir_name_from_module_ID( MO_ID ) for MO_ID in self._path_methods.keys()] )
        self._out_rows.append( header_row )
        # Methods
        [self._add_method_row( method_name )
         for count in range( count_max, 0, -1 ) if count in method_name_occurrences.keys()
         for method_name in sorted( method_name_occurrences[count] )
         ]
        # Output
        csvm.write_rows( self._out_rows, open_mode='w', data_path=f'{session.output_dir}Compare.csv' )
        return Result( text=f'{len( self._out_rows ) - 1} different methods found in {len(method_names)} methods.',
                       severity=MessageSeverity.Completion )

    def _list_methods(self, module_ID):
        self._path_methods[module_ID] = [row_to_obj( Table.Functions, row ) for row in self._db.fetch(
            Table.Functions, where=[Att( FD.MO_ID, value=module_ID )] )]

    def _add_method_row(self, method_name):
        # List method hashes for all paths
        hash_codes = {MO_ID: EMPTY for MO_ID in self._path_methods.keys()}
        for MO_ID, Functions in self._path_methods.items():
            for F in Functions:
                if method_name == F.Function_name:
                    hash_codes[MO_ID] = F.Hash
                    break
        # Count unique method hashes
        hash_counts = {}
        hash_codes_filled = [h for h in hash_codes.values() if h]
        for h in hash_codes_filled:
            if h not in hash_counts:
                hash_counts[h] = 1
            else:
                hash_counts[h] += 1
        method_count = len( hash_codes_filled )
        max_equal = max( v for v in hash_counts.values() )
        path_count = len( self._path_methods.keys() )
        if CM.get_config_item( CF_LIST_DIFF_ONLY ) == TRUE and path_count == method_count == max_equal:
            return
        # Add the row
        out_row = [method_name, method_count, max_equal]
        out_row.extend( [h for h in hash_codes.values()] )
        self._out_rows.append( out_row )

    @staticmethod
    def _insert_repository(dir_name):
        # Add repo
        if repository_IO.insert( dir_name=dir_name ) == 0:
            raise GeneralException( f'{__name__}: Repository could not be inserted.' )

    def _get_repo_dir_name_from_module_ID(self, MO_ID) -> str:
        """
        Truncate the leading namespace.
        If a root function has been searched, there is no namespace.
        Then truncate the leading part common to all repos.
        """
        MO = iom.get_obj_by_ID( Table.Modules, MO_ID )
        # Find common base
        repo_dir_p = EMPTY
        s = 0
        for repo_dir in self._repo_dirs:
            if repo_dir_p:
                for i in range(min(len(repo_dir), len(repo_dir_p))):
                    if repo_dir[i] != repo_dir_p[i]:
                        s = min(i, s) if s > 0 else i
                        break
            repo_dir_p = repo_dir
        for repo_dir in self._repo_dirs:
            # a. Base name
            if MO.Namespace.startswith( repo_dir ):
                return os.path.basename( repo_dir[:-1] )
            # b. Else base path, when root source file has no namespace
        return MO.Namespace[s:]
