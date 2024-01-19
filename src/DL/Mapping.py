from src.DL.Model import Model
from src.GL.Const import EMPTY
from src.GL.GeneralException import GeneralException

PGM = 'Mapping'

model = Model()


class Mapping(object):
 
    def __init__(self):
        pass

    @staticmethod
    def get_mapping(to_table, from_table):
        """
        Create "to_table" attributes, with 0-based index of corresponding "from_table" attributes (or -1)
        :return: mappings [[to_attribute_name, from_index]]
        """
        # Example:
        # To                          From
        # FindingsWork attributes     Findings index (or -1)
        # -----------------------     ----------------------
        # [FieldDef.FW_Project,        -1
        # [FieldDef.FI_Status,          4
        # [FieldDef.SP_Pattern_name,   10
        # [FieldDef.FI_File_dir,        5
        # [FieldDef.FI_File_name,       6
        # [FieldDef.FI_File_ext,       11
        # [FieldDef.FI_Line_no,         7
        # [FieldDef.FI_Pos,             8
        # [FieldDef.FI_Source_line,     9
        # [FieldDef.FI_Escaped,        13

        mapping = []
        # List "from_table" attribute names in column order.
        from_table_attributes = []
        for col_number, att in model.FFD[from_table].items():
            from_table_attributes.append(att.name)

        # Create to_table attribute names, with index of from_table attributes (or -1)
        for col_number, att in model.FFD[to_table].items():
            if att.name in from_table_attributes:
                mapping.append([att.name, from_table_attributes.index(att.name)])
            else:
                mapping.append([att.name, -1])

        return mapping

    @staticmethod
    def map_rows(rows, table_name) -> list:
        """
        Migrate list contents based on a table definition, using column header as a reference.
        Purpose: If in DBDriver csv import fails when e.g. attributes are added in the DB,
        the new attributes are added in the row.

        :param rows: Rows to be mapped
        :param table_name: Table to be mapped to
        :return: Mapped row-list

        Example: MarkedFindings
        Recommendation, PolicyCode, Score, Details, Reference are added in Model and Table.
        Csv file must be mapped, new fields are filled with EMPTY.
                                Csv                Colnos
        Table = out_att_dict    Header             Csv   Out_rows
        ---------------------------------------------------------
        0  Id                   Id
        - - - - - - - -
        1  PatternName          Patternname         1       0
        2  FileName             Filename            2       1
        3  SourceLine           Sourceline          3       2
        4  Reason_Or_Question   Reason_Or_Question  4       3
        5  Recommendation                                   4
        6  Answer               Answer              5       5
        7  Status               Status              6       6
        8  PolicyCode                                       7
        9  Score                                            8
        10 Details                                          9
        11 Reference                                       10
        """
        if rows is None or len( rows ) == 0 or len( rows[0] ) == 0:
            return []

        # Correction for is the csv file contains an Id
        zero_based = False if rows[0][0].lower() == 'id' else True

        # Table definition
        out_att_dict = model.get_att_order_dict( table_name, zero_based=zero_based, LC=True )
        if not out_att_dict:
            return []

        # Define csv col_nos to map (skip Id)
        header_row = [c.lower() for c in rows[0]]
        tbl_csv_colno_map = {}
        i = 0
        for title in header_row:
            if title in out_att_dict:
                tbl_csv_colno_map[out_att_dict[title]] = i
            i += 1
        if not tbl_csv_colno_map:
            return []

        # New header via Table definition
        out_rows = [model.get_att_names( table_name, strict=False )]
        out_col_nos = out_att_dict.values()

        # Populate via Map
        first = True
        for row in rows:

            # Skip csv header
            if first:
                first = False
                continue

            # Add row
            out_row = []
            for c in out_col_nos:
                if c in tbl_csv_colno_map:
                    out_row.append( row[tbl_csv_colno_map[c]] )
                else:
                    out_row.append( EMPTY )
            out_rows.append( out_row )

        return out_rows

    @staticmethod
    def get_default_dict(inp_table_name, out_table_name):
        default_dict = {}
        # 1. Get Attributes by column name
        inp_att_dict = model.get_att_by_name_dict(inp_table_name)
        out_att_dict = model.get_att_by_name_dict(out_table_name)
        # 2. Create default_dict of all out-columns not in inp-columns
        for col_name, att in out_att_dict.items():
            if col_name not in inp_att_dict:
                c = model.get_zero_based_column_number(out_table_name, col_name)
                default_dict[c] = att.default
        return default_dict

    def migrate_rows_by_table_defs(self, inp_rows, inp_table_name, out_table_name, id_in_rows=True, subst_dict=None):
        """
        Migrate a row-list based on input table definition to a row-list based on output table definition.
        Precondition: All attributes (columns in inp_rows + default_dict) in the out_table must be present.
        E.g. inp_rows "Findings" is a subset of and mapped to "FindingsWork".

        :param id_in_rows: Read from table: Id is extra. (Unittest uses .csv files without Id).
        :param inp_rows: Rows to be mapped
        :param inp_table_name: Table name to retrieve format for inp_rows
        :param out_table_name: Table name to retrieve format for out_rows
        :param subst_dict: output_colno : input_colno  e.g. substitute FI.Line_no by FA.Line_no_from
        :return: Mapped row-list
        """
        method = 'migrate_rows_by_table_defs'
        if id_in_rows:
            Id_count = 1
        else:
            Id_count = 0

        """
        Check input
        """
        # 1. Rows must be present
        if inp_rows is None or len(inp_rows) == 0:
            return []

        # 2. Columns must be present
        inp_col_count = len(inp_rows[0])
        if inp_col_count == 0:
            return []

        # 3. Get the output defaults
        default_dict = self.get_default_dict(inp_table_name, out_table_name)

        # 4. All output columns must be available to create the output rows.
        #   Get the column mapping (dictionary of column numbers)
        #   E.g. { 0: -1, 1: 0, 2: -1, 3: 2,... }
        #   The "-1" values must then be present in the default_dict.

        # 0-based mapping example:

        # FindingsWork          Findings
        #  (output)            (in model)
        # ------------------   ----------
        #  0: ProjectId          -1
        #  1: ProjectVersion     -1
        #  2: ResultStatus       -1
        #  3: Status              3
        #  4: RefersToId         -1
        #  5: RefersToVersion    -1
        #  6: PatternName         9
        #  7: Purpose            10
        #  8: Classification     11
        #  9: OWASP              12
        # 10: Severity           13
        # 11: FileDir             4
        # 12: FileName            5
        # 13: FileExt            14
        # 14: LineNo              6
        # 15: Pos                 7
        # 16: SourceLine          8
        # 17: FileHash           -1
        # 18: Escaped            -1

        output_to_input_column_mapping = \
            self.get_column_mapping_by_table(
                base_table=out_table_name,
                compare_table=inp_table_name,
            )

        for out_col_no, inp_col_no in output_to_input_column_mapping.items():
            if inp_col_no == -1:
                if default_dict is None or out_col_no not in default_dict:
                    self._error_control(
                        method,
                        'Output column {}[{}] can not be mapped. It must exist either in the '
                        'input table or in the specified defaults dictionary.'.format(
                            out_table_name, str(out_col_no)) )
                    return []
        """
        out rows = columns in sequence of the out_definition, populated with matching inp_row values.
        If no match, the value is substituted by a default value. 
        """
        inp_row_len = len(inp_rows[0])
        out_rows = []
        for row in inp_rows:
            out_row = []
            # Dict [out_colno: inp_colno] is ordered by out_colno's.
            for out_col_no, inp_col_no in output_to_input_column_mapping.items():
                if subst_dict and out_col_no in subst_dict:
                    inp_cell_value = row[subst_dict[out_col_no] + Id_count]
                elif inp_col_no == -1:
                    inp_cell_value = default_dict[out_col_no]
                else:
                    inp_col_no += Id_count  # Id-correction: In case of table rows, id is present.
                    if inp_col_no >= inp_row_len:
                        self._error_control(
                            method, f'Table {inp_table_name} column {str(inp_col_no)} (0-based) '
                                    'does not exist in input list.')
                        return []
                    inp_cell_value = row[inp_col_no]
                out_row.append(inp_cell_value)
            out_rows.append(out_row)
        return out_rows

    @staticmethod
    def migrate_rows(rows, table_name) -> list:
        """
        Migrate list contents based on a table definition, using column header as a reference.
        Purpose: If in DBDriver csv import fails when e.g. attributes are added in the DB,
        the new attributes are added in the row.

        :param rows: Rows to be mapped
        :param table_name: Table to be mapped to
        :return: Mapped row-list

        Example: MarkedFindings
        Recommendation, PolicyCode, Score, Details, Reference are added in Model and Table.
        Csv file must be mapped, new fields are filled with EMPTY.
                                Csv                Colnos
        Table = out_att_dict    Header             Csv   Out_rows
        ---------------------------------------------------------
        0  Id                   Id
        - - - - - - - -
        1  PatternName          Patternname         1       0
        2  FileName             Filename            2       1
        3  SourceLine           Sourceline          3       2
        4  Reason_Or_Question   Reason_Or_Question  4       3
        5  Recommendation                                   4
        6  Answer               Answer              5       5
        7  Status               Status              6       6
        8  PolicyCode                                       7
        9  Score                                            8
        10 Details                                          9
        11 Reference                                       10
        """
        if rows is None or len( rows ) == 0 or len(rows[0]) == 0:
            return []

        # Correction for is the csv file contains an Id
        zero_based = False if rows[0][0].lower() == 'id' else True

        # Table definition
        out_att_dict = model.get_att_order_dict( table_name, zero_based=zero_based, LC=True )
        if not out_att_dict:
            return []

        # Define csv col_nos to map (skip Id)
        header_row = [c.lower() for c in rows[0]]
        tbl_csv_colno_map = {}
        i = 0
        for title in header_row:
            if title in out_att_dict:
                tbl_csv_colno_map[out_att_dict[title]] = i
            i += 1
        if not tbl_csv_colno_map:
            return []

        # New header via Table definition
        out_rows = [model.get_att_names( table_name, strict=False )]
        out_col_nos = out_att_dict.values()

        # Populate via Map
        first = True
        for row in rows:

            # Skip csv header
            if first:
                first = False
                continue

            # Add row
            out_row = []
            for c in out_col_nos:
                if c in tbl_csv_colno_map:
                    out_row.append(row[tbl_csv_colno_map[c]])
                else:
                    out_row.append(EMPTY)
            out_rows.append(out_row)

        return out_rows

    def migrate_rows_cross_table(self, inp_rows, inp_att_dict, out_att_dict, inp_contains_id=True, header_row=False):
        """
        Migrate a row-list based on an input dict to a row-list based on an output dict.
        :param inp_contains_id: input from file
        :param inp_rows: Rows to be mapped
        :param inp_att_dict: Format of inp_rows
        :param out_att_dict: Format for out_rows (containing default values too)
        :param header_row: Contains header row?
        :return: Mapped row-list
        """
        method = 'migrate_rows_cross_table'
        """
        Check input
        """
        # 1. Rows must be present
        if inp_rows is None or len( inp_rows ) == 0:
            return []

        # 2. Input columns must be present, and as many as in inp_att_dict.
        if inp_contains_id:
            length_correction = 1
        else:
            length_correction = 0

        inp_col_count = len( inp_rows[0] )
        if inp_col_count == 0 or inp_col_count - length_correction != len( inp_att_dict ):
            return []

        #   Get the non-0-based column mapping (dictionary of column numbers)
        #   E.g. { 1: -1, 2: 1, 3: -1, 4: 2,... }
        output_to_input_column_mapping = \
            self.__get_column_mapping_by_dict( out_att_dict, inp_att_dict )

        """
        out rows = columns in sequence of the out_definition, populated with matching inp_row values.
        If no match, the value is substituted by the default value. 
        """
        out_rows = []
        out_row = []

        # Header row
        for col_no, att in out_att_dict.items():
            out_row.append( out_att_dict[col_no].name )
        out_rows.append( out_row )

        # Detail rows
        i = 0
        row = []
        try:
            for row in inp_rows:
                i += 1
                if header_row and i == 1:
                    continue
                out_row = []
                for out_col_no, inp_col_no in output_to_input_column_mapping.items():
                    if inp_col_no == -1:
                        inp_cell_value = out_att_dict[out_col_no].default
                    else:
                        inp_cell_value = row[inp_col_no]
                    out_row.append( inp_cell_value )
                out_rows.append( out_row )
            return out_rows
        except IndexError as e:
            self._error_control( method, f'Error at row {i}: {e.args[0]}. row is {row}' )
            return []

    @staticmethod
    def __get_column_mapping_by_dict(out_att_dict, inp_att_dict):
        """
        Map to non-0-based column numbers, e.g {1:-1, 2:1, 3:2,...]
        """
        out_map = {}
        inp_col_no_by_name_dict = {}

        # get the (non-zero-based) column numbers by name
        for key, att in inp_att_dict.items():
            inp_col_no_by_name_dict[att.name] = int(key)

        for col_no, att in out_att_dict.items():
            if att.name in inp_col_no_by_name_dict:
                out_map[col_no] = inp_col_no_by_name_dict[att.name]
            else:
                out_map[col_no] = -1
        return out_map

    def get_column_mapping_by_table(self, base_table, compare_table):
        # Example:

        # Base                           Compare             Output (0-base)
        # -----------------------        -------- --------  ----------
        #  1 FieldDef.PJ_Project         -1     { 1: -1,   { 0: -1,
        #  2 FieldDef.FP_Project_version  0       2: -1,     1: -1,
        #  3 FieldDef.FI_Status           5       3:  5      2:  4,
        #  ...                                     ...}        ...}

        # Get both 0-based dictionaries of [attribute_name: index]
        method = 'get_column_mapping_by_table'
        base_mapping = model.get_att_order_dict( base_table )
        compare_mapping = model.get_att_order_dict( compare_table )

        if base_mapping == {}:
            self._error_control( method, 'Table "{}" does not exist in the model.'.format( base_table ) )
            return {}
        if compare_mapping == {}:
            self._error_control( method, 'Table "{}" does not exist in the model.'.format( compare_table ) )
            return {}

        # Map to 0-based row numbers, e.g {0:-1, 1:-1, 2:9,...]
        base_compare_map = {}
        for attribute_name, col_no in base_mapping.items():
            if attribute_name in compare_mapping:
                base_compare_map[col_no] = compare_mapping[attribute_name]
            else:
                base_compare_map[col_no] = -1
        return base_compare_map

    @staticmethod
    def _error_control(routine, error_text=EMPTY):
        raise GeneralException(f'{PGM}.{routine}: {error_text}')
