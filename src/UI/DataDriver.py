
from src.DL.DBDriver.Att import Att
from src.DL.DBDriver.Enums import FetchMode, OrderType
from src.DL.Model import Model, FD as FD
from src.GL.Const import ASTERISK


class DataDriver( object ):

    def __init__(self, db):
        self._db = db

    def get_table_data(self,
                       table_name,
                       col_names=None,
                       where=None,
                       order_by=None,
                       mode=FetchMode.WholeTable,
                       add_header=True
                       ):
        if not self._db:
            return []

        # Order by
        order_by = [[Att( FD.ID ), OrderType.DESC]] if order_by and order_by == OrderType.DESC else None
        # Get header
        data = [Model().get_att_names(table_name, include_id=True, strict=False)] if add_header and col_names else []
        # Add detail rows
        data.extend(self._db.fetch(
            table_name,
            mode=mode,
            where=where,
            order_by=order_by)
        )
        # Select columns
        out_rows = []
        if col_names:
            column_dict = Model().get_att_order_dict(table_name, zero_based=False)
            for data_row in data:
                out_rows.append( [data_row[column_dict[name]] for name in col_names] )
            return out_rows
        else:
            out_rows = data
        return out_rows

    @staticmethod
    def get_table_names():
        return Model().DB_tables

    def get_column(self, table_name, col_name, where=None, add_all_entry=True) -> list:
        rows = (self.get_table_data(table_name, where=where))
        col_no = Model().get_zero_based_column_number(table_name, col_name)
        data = sorted([r[col_no + 1] for r in rows])
        if add_all_entry:
            data.extend([ASTERISK])
        return sorted(data)
