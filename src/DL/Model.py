from src.DL.DBDriver.Att import Att, sanitize_value
from src.DL.DBDriver.AttType import AttType
from src.DL.DBDriver.Functions import quote
from src.DL.Table import Table
from src.DL.Enums import Mnemonics
from src.GL.Enums import Appearance
from src.GL.GeneralException import GeneralException

NAME = 'Name'
DESC = 'Description'
TYPE = 'Type'
VALUE = 'Value'

PGM = 'Model'
EMPTY = ''
table = Table()

KEY_DELIMITER = '|'

# Mnemonics: including CO
mnemonics = [Mnemonics.RP, Mnemonics.CP, Mnemonics.CO, Mnemonics.MO, Mnemonics.CL, Mnemonics.FU, Mnemonics.SU]

table_codes = {
    Mnemonics.RP: Table.Repositories,
    Mnemonics.CO: Table.Containers,
    Mnemonics.MO: Table.Modules,
    Mnemonics.CL: Table.Classes,
    Mnemonics.FU: Table.Functions,
    Mnemonics.SU: Table.Summary
}


# Index definitions
class IndexDef(object):
    FU_on_Logical_Key = 'FU_on_Logical_Key'
    FU_IX_on_Type = 'FU_IX_on_Type'
    FU_IX_on_Logical_key = 'FU_IX_on_Logical_key'
    CL_on_Logical_Key = 'CL_on_Logical_Key'

    # PK
    CP_PK = 'CP_PK'
    CO_PK = 'CO_PK'
    MO_PK = 'MO_PK'
    CL_PK = 'CL_PK'
    FU_PK = 'FU_PK'
    RP_PK = 'RP_PK'
    SU_PK = 'SU_PK'


# Field definition
class FD( object ):
    ID = 'Id'
    No = 'No'
    SeqNo = 'SeqNo'
    ErrorMessage = 'ErrorMessage'
    Deleted = 'Deleted'

    # FFD
    FF_TableName = 'TableName'
    FF_AttName = 'AttributeName'
    FF_AttType = 'AttributeType'
    FF_AttLength = 'AttributeLength'
    FF_Derived = 'Derived'

    RP_Dir_name = 'DirName'

    # XRef
    # ----
    # Container
    CO_ID = 'ContainerID'
    CO_Imported_ID = 'CO_Imported_ID'
    CO_ContainerName = 'ContainerName'
    CO_ContainerType = 'ContainerType'
    CO_ParentName = 'ParentName'
    CO_ParentType = 'ParentType'

    # Modules
    MO_ID = 'ModuleID'
    MO_Namespace = 'Namespace'
    MO_ModuleName = 'ModuleName'
    MO_Filename = 'Filename'

    # Class
    CL_ClassName = 'ClassName'
    CL_LineNo = 'LineNo'

    # Functions (Method, function)
    FU_FunctionName = 'FunctionName'
    FU_FunctionType = 'FunctionType'
    FU_LineNo_start = 'LineNoStart'
    FU_LineNo_end = 'LineNoEnd'
    FU_Hash = 'Hash'

    # Summary
    SU_Count = 'Count'
    SU_MaxEqual = 'MaxEqual'


class Model(object):
    @property
    def error_message(self):
        return self._error_message

    @property
    def FFD(self):
        return self._FFD

    @FFD.setter
    def FFD(self, value):
        self._FFD = value

    @property
    def DB_tables(self):
        return self._DB_tables

    @DB_tables.setter
    def DB_tables(self, value):
        self._DB_tables = value

    def __init__(self):
        self._table = Table
        self._error_message = EMPTY

        """
        Table definitions
        """
        self._Repositories = {
            1: Att( FD.RP_Dir_name ),  # pk-1
        }

        self._Containers = {
            1: Att( FD.MO_Namespace ),  # pk-1
            2: Att( FD.MO_ModuleName ),  # pk-2
            3: Att( FD.CO_ContainerType ),  # pk-3
            4: Att( FD.CO_ContainerName ),  # pk-4
            5: Att( FD.CO_ParentName ),  # pk-5
            6: Att( FD.CO_ParentType ),  # pk-6
            7: Att( FD.FU_FunctionType )
        }

        self._Modules = {
            1: Att( FD.MO_Namespace ),
            2: Att( FD.MO_ModuleName ),
            3: Att( FD.MO_Filename ),
        }

        self._Classes = {
            1: Att( FD.CO_ID, type=AttType.Int  ),
            2: Att( FD.MO_Namespace ),  # redundant
            3: Att( FD.MO_ModuleName ),  # redundant
            4: Att( FD.CL_ClassName ),  # redundant
            5: Att( FD.CL_LineNo, type=AttType.Int ),
        }

        self._Functions = {
            1: Att( FD.CO_ID, type=AttType.Int ),  # pk-1
            2: Att( FD.MO_ID, type=AttType.Int ),  # redundant
            3: Att( FD.MO_Namespace ),  # redundant
            4: Att( FD.MO_ModuleName ),  # redundant
            5: Att( FD.CO_ParentName ),  # redundant
            6: Att( FD.CO_ParentType ),  # redundant (module or class)
            7: Att( FD.FU_FunctionName ),
            8: Att( FD.FU_FunctionType ),  # Property, function, method
            9: Att( FD.FU_LineNo_start, type=AttType.Int ),
            10: Att( FD.FU_LineNo_end, type=AttType.Int ),
            11: Att( FD.FU_Hash ),
        }

        self._Summary = {
            1: Att(FD.FU_FunctionName),
            2: Att(FD.SU_Count, type=AttType.Int),
            3: Att(FD.SU_MaxEqual, type=AttType.Int),
        }
        """
        Database definitions
        """
        self._FFD_FFD = {
            1: Att( FD.FF_TableName ),
            2: Att( FD.FF_AttName ),
            3: Att( FD.FF_AttType ),
            4: Att( FD.FF_AttLength, type=AttType.Int ),
            5: Att( FD.FF_Derived, type=AttType.Bool )
        }

        self._FFD = {
            Table.Containers: self._Containers,
            Table.Modules: self._Modules,
            Table.Classes: self._Classes,
            Table.Functions: self._Functions,
            Table.Repositories: self._Repositories,
            Table.Summary: self._Summary
        }

        self._DB_tables = [
            Table.Containers,
            Table.Modules,
            Table.Classes,
            Table.Functions,
            Table.Repositories,
            Table.Summary
        ]

        """
        Index definitions
        """
        self._PK_indexes = {
            Table.Containers: IndexDef.CO_PK,
            Table.Modules: IndexDef.MO_PK,
            Table.Classes: IndexDef.CL_PK,
            Table.Functions: IndexDef.FU_PK,
            Table.Repositories: IndexDef.RP_PK,
            Table.Summary: IndexDef.SU_PK,
        }

        self._Indexes = {
            Table.Repositories: {
                IndexDef.RP_PK:
                    [FD.RP_Dir_name]
            },

            Table.Containers: {
                IndexDef.CO_PK:
                    [FD.MO_Namespace,
                     FD.MO_ModuleName,
                     FD.CO_ContainerType,
                     FD.CO_ContainerName,
                     FD.CO_ParentName,
                     FD.CO_ParentType
                     ]
            },
            Table.Modules: {
                IndexDef.MO_PK:
                    [FD.MO_Namespace,
                     FD.MO_ModuleName,
                     ]
            },

            Table.Classes: {
                IndexDef.CL_PK:
                    [FD.CO_ID],
                IndexDef.CL_on_Logical_Key:
                    [FD.MO_Namespace,
                     FD.MO_ModuleName,
                     FD.CL_ClassName,
                     ],
            },

            Table.Functions: {
                IndexDef.FU_PK:
                    [FD.CO_ID],
                IndexDef.FU_on_Logical_Key:
                    [FD.MO_Namespace,
                     FD.MO_ModuleName,
                     FD.CO_ParentName,
                     FD.FU_FunctionName,
                     ],
                IndexDef.FU_IX_on_Type:
                    [FD.FU_FunctionType,
                     FD.MO_Namespace,
                     FD.MO_ModuleName,
                     FD.CO_ParentName,
                     FD.FU_FunctionName,
                     ],
            },
            Table.Summary: {
                IndexDef.SU_PK:
                    [FD.FU_FunctionName]
            }
        }

    def is_valid(self) -> bool:
        """
        Only check some "relational" consistency.
        """
        # Check PK definition
        for t, idx in self._PK_indexes.items():
            att_names_pk = self._Indexes[t][idx]
            if not self._FFD.get( t ):
                self._error_message = f'{PGM}: Table "{t}" does not exist in FFD.'
                return False
            att_names = self.get_att_names(t)
            for att_name in att_names_pk:
                if att_name not in att_names:
                    self._error_message = f'{PGM}: PK name "{att_name}" does not exist in table "{t}" definition.'
                    return False
        # File mnemonics
        for table_name in self.FFD.keys():
            if table_name not in table_codes.values():
                self._error_message = f'{PGM}.is_valid: Table "{table_name}" does not have a mnemonic.'
                return False
        return True

    def get_FFD(self):
        return self._FFD_FFD

    def get_model(self, table_name):
        if table_name in self._FFD:
            model = self._FFD[table_name]
        else:
            model = {}
        return model

    @staticmethod
    def get_table_name_from_code(code) -> str:
        return table_codes[code] if code and code in table_codes else EMPTY

    @staticmethod
    def get_table_name_from_fk_name(att_name):
        """
        E.g. returns "Element" from "ElementId"
        """
        p = att_name.find('Id') if att_name else -1
        return f'{att_name[:p]}' if p > 0 else EMPTY

    def get_indexes(self, table_name) -> dict:
        return self._Indexes[table_name] if table_name in self._Indexes else {}

    @staticmethod
    def get_where(**kwargs):
        return [Att( name_from_arg( k ), value=v ) for k, v in kwargs.items()]

    def get_attributes(self, table_name):
        attributes = {}
        if table_name in self._FFD:
            attributes = self._FFD[table_name]
        return attributes

    def get_att(self, table_name, att_name, appearance=None) -> Att or None:
        for col_number, att in self._FFD[table_name].items():
            if att.name == att_name:
                if appearance and hasattr(Appearance, appearance):
                    att.appearance = appearance
                return att
        return None

    def get_att_names(self, table_name, include_id=False, strict=True, LC=False):
        """
        To get the headings (column names) in designed sequence
        """
        att_names = []
        first = True
        for att in self._FFD[table_name].values():
            if first and include_id:
                first = False
                att_names.append( FD.ID )
            if strict:
                att_names.append( att.name )
            else:
                att_names.append( att.name.title() )
        return [att.lower() for att in att_names] if LC else att_names

    def get_att_by_name_dict(self, table_name):
        """
        To get attributes by column names
        """
        att_dict = {}
        for key, att in self._FFD[table_name].items():
            att_dict[att.name] = att
        return att_dict

    def get_att_order_dict(self, table_name, zero_based=True, LC=False) -> dict:
        """
        To get the column numbers at the column names
        """
        att_dict = {}
        for key, att in self._FFD[table_name].items():
            if zero_based:
                att_dict[_LC( att.name, LC )] = int( key ) - 1
            else:
                att_dict[_LC( att.name, LC )] = int( key )
        return att_dict

    def get_zero_based_column_number(self, table_name, col_name):
        """
        :return: 0-based row number
        """
        for col_number, att in self._FFD[table_name].items():
            if att.name == col_name:
                return int(col_number) - 1
        return -1

    def get_column_number(self, table_name, col_name, zero_based=False) -> int or None:
        """
        :return: 0-based row number
        """
        table_def = self._FFD_FFD if table_name == 'FFD' else self._FFD[table_name]
        for col_number, att in table_def.items():
            if att.name == col_name:
                return int( col_number ) - 1 if zero_based else int( col_number )
        return None

    def validate_row(self, table_name, row, isFFDTable=True, has_id=False):
        method = 'validate_row'

        Id_corr = 1 if has_id else 0

        # Validate input
        if table_name not in self._FFD:
            if isFFDTable:
                return f'{PGM}.{method}: Table "{table_name}" does not exist in FFD.'
            else:
                return EMPTY

        atts = self._FFD[table_name]
        if len(row) != len(atts) + Id_corr:
            return f'{PGM}.{method}: {table_name} row length ({len(row)}) <> FFD length ({len(atts)}).'

        # Sanitize row
        for col_number, att in self._FFD[table_name].items():
            c = col_number - 1 + Id_corr  # 0-based + optional skip of Id
            row[c] = sanitize_value( row[c], att.type, att.length )

        return EMPTY


def where_atts_to_string(where) -> str:
    where_clause = EMPTY
    where_or_and = 'WHERE '
    for a in where:
        a.value = quote(a.value) if a.type in (AttType.Varchar, AttType.Text) else a.value
        where_clause = f'{where_clause}{where_or_and}{a.name}{a.relation}{a.value}'
        where_or_and = ' AND '
    return where_clause


def _LC(item, LC):
    return item.lower() if LC else item


def arg_from_name(name) -> str:
    try:
        # Remove mnemonic like MO_Namespace
        name = remove_mnemonic(name)
        # Still "_": nothing to do.
        if '_' in name:
            return name.lower()
        # Id is a special case.
        if name.lower() == 'id':
            return 'ID'
        # Make as lowercase, Add "_" where appropriate
        count, prv_char = 0, EMPTY
        out = []
        name = list(name)
        name[0] = name[0].lower()
        for i in name:
            # Insert "_" but prevent CountCRHigh to result in "count_c_r_high"
            if i.isupper() and count > 0 and not prv_char.isupper() and not prv_char == '_':
                out.append( '_' )
            out.append( i.lower() )
            prv_char = name[count]
            count += 1
    except (ValueError, Exception) as e:
        raise GeneralException(f'{__name__}: "{name}" could not be formatted. Cause: {e}')
    return ''.join( out )


def name_from_arg(arg_name) -> str:
    out = []
    name = list(arg_name)
    upper = True  # 1st always uppercase
    for i in name:
        if i == '_':  # Ignore "_"
            upper = True
        else:
            if upper:
                i = i.upper()
                upper = False
            out.append( i )
    out_name = ''.join( out )
    if not hasattr(FD, add_mnemonic(out_name)):
        raise GeneralException(f'{__name__}.model_name: "{arg_name}" could not be mapped. '
                               f'Cause: "{out_name}" does not exist in FD.')
    return out_name


def add_mnemonic(name) -> str:
    for mn in mnemonics:
        if hasattr( FD, f'{mn}_{name}' ):
            return f'{mn}_{name}'
    return name


def remove_mnemonic(name) -> str:
    # Remove mnemonic like MO_Namespace
    p = name.find( '_' )
    return name[p + 1:] if p > -1 else name


arg_names = {remove_mnemonic(name): arg_from_name( name ) for name in dir( FD ) if not name.startswith( '__' )}
