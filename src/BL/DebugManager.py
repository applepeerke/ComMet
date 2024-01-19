from src.GL.BusinessLayer.CsvManager import CsvManager
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import EMPTY
from src.GL.DataLayer.Result import Result
from src.GL.Enums import ResultCode, MessageSeverity

csvm = CsvManager()


class Singleton:
    """ ConfigManager """

    class DebugManager( object ):

        @property
        def method_names_dict(self):
            return self._method_names_dict

        def __init__(self):
            # Repo paths
            self._method_names_dict = {}

        def add_method_lines(self, ns, lines):
            """
            For a repository, add the method snippet.
            """
            self._method_names_dict[ns] = lines

        def evaluate_first_3_methods(self) -> Result:
            """
            For max. 3 repositories, compare their methods.
            """
            print(f'DEBUG mode - {Session().debug_method_name}')
            print('----------------------------')
            keys = [k for k in self._method_names_dict.keys() ]
            values = [k for k in self._method_names_dict.values() ]
            if len(keys) < 2:
                return Result(ResultCode.Error, 'Too few method names to compare')

            if not all(len(v) == len(values[0]) for v in values):
                print(f'No. of lines is unequal, {", ".join([str(len(v)) for v in values])}. See csv file.')
                self._to_csv(keys, values)

            # Legend
            [print( f'{i+1}={keys[i]}' ) for i in range(len(keys))]

            count = 0
            for i in range(len(self._method_names_dict[keys[0]])-1):
                l1 = self._method_names_dict[keys[0]][i]
                l2 = self._method_names_dict[keys[1]][i] if i < len(values[1]) else EMPTY
                l3 = self._method_names_dict[keys[2]][i] if (len(keys) > 2 and i < len(values[2]) ) else EMPTY
                if l1 != l2 or (l3 and l1 != l3):
                    count += 1
                    print(f'Line {i} is unequal:')
                    print(f'   1: "{l1}"')
                    print(f'   2: "{l2}"')
                    if len( keys ) > 2:
                        print( f'   3: "{l3}"' )

            text = f'{count} lines are different.' if count > 0 else 'No differences found.'
            return Result( text=text, severity=MessageSeverity.Completion )

        @staticmethod
        def _to_csv(keys, values):
            rows = [k for k in keys]
            for i in range(len(values[0])):
                cell_1 = values[0][i]
                cell_2 = values[1][i] if i < len(values[1]) else EMPTY
                cell_3 = values[2][i] if len(values) > 2 and i < len(values[2]) else EMPTY
                rows.append([cell_1, cell_2, cell_3])
            # Rest of 2nd
            if len(values[1]) > len(values[0]):
                for i in range( len(values[0]), len(values[1]) ):
                    cell_1 = EMPTY
                    cell_2 = values[1][i]
                    cell_3 = values[2][i] if len( values ) > 2 and i < len( values[2] ) else EMPTY
                    rows.append( [cell_1, cell_2, cell_3] )
            # Rest of 3rd
            if len(values[2]) > len(values[0]) and len(values[2]) > len(values[1]):
                for i in range( max(len(values[0]), len(values[1])), len(values[2]) ):
                    cell_1 = EMPTY
                    cell_2 = EMPTY
                    cell_3 = values[2][i]
                    rows.append( [cell_1, cell_2, cell_3] )
            # Write
            csvm.write_rows(
                rows=rows,
                open_mode='w',
                data_path=f'{Session().output_dir}Debug_{Session().debug_method_name}')

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.DebugManager()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr( self.__instance, attr )

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr( self.__instance, attr, value )
