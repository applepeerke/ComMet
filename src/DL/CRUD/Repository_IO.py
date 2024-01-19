from src.DL.DBDriver.Att import Att
from src.DL.Table import Table
from src.DL.Model import FD, Model
from src.GL.Const import EMPTY
from src.GL.BusinessLayer.SessionManager import Singleton as Session

TABLE = Table.Repositories
att_names = Model().get_att_names( TABLE )


class Repository_IO( object ):

    def __init__(self):
        pass

    @staticmethod
    def insert(dir_name) -> int or None:

        pk = [ Att( FD.RP_Dir_name, value=dir_name ), ]
        row = []

        for att_name in att_names:
            if att_name == FD.RP_Dir_name:
                row.append(dir_name) or EMPTY
            else:
                row.append(EMPTY)

        return Session().db.check_then_insert( TABLE, row, where=pk, pgm=__name__ )
