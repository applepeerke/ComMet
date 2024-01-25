import unittest

from src.DL.DBInitialize import DBInitialize as DBInit
from src.DL.Model import Model
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import EMPTY

session = Session()
session.set_paths(unit_test=True)
dbInit = DBInit()
model = Model()
DB = EMPTY
db_consistent = False
NOT_CONSISTENT = 'Database is not consistent.'


# -----------------------------------------------------------------------------------------------------------------
#   Class functions
# -----------------------------------------------------------------------------------------------------------------


def initialize_test() -> bool:
    global db_consistent
    if not session.db:
        dbInit.connect()
    if not session.db:
        return False
    if not dbInit.is_consistent():
        return False

    for t in model.DB_tables:
        session.db.clear(t)
    return True


class XRefTestCase(unittest.TestCase):

    # -----------------------------------------------------------------------------------------------------------------
    #   T e s t s
    # -----------------------------------------------------------------------------------------------------------------

    def test_TC00_SetUp_Db(self):
        global DB
        self.assertTrue(initialize_test(), msg=NOT_CONSISTENT)
        for t in model.DB_tables:
            self.assertTrue(session.db.file_exists(t))


# -----------------------------------------------------------------------------------------------------------------
#   M a i n
# -----------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
