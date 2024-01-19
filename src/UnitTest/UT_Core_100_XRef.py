import os
import unittest

from src.DL.DBInitialize import DBInitialize as DBInit
from src.DL.Model import Model
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import App as APP, EMPTY
from src.GL.Validate import normalize_dir

session = Session()
dbInit = DBInit()
model = Model()
session.set_paths(unit_test=True)
UT_input_dir = session.UT_dir
DB = EMPTY
db_consistent = False
NOT_CONSISTENT = 'Database is not consistent.'


# -----------------------------------------------------------------------------------------------------------------
#   Class functions
# -----------------------------------------------------------------------------------------------------------------


def initialize_test() -> bool:
    global DB, db_consistent
    if not session.db:
        dbInit.connect( DB )
    if not session.db:
        return False
    if not dbInit.is_consistent():
        return False

    for t in model.DB_tables:
        session.db.clear( t )
    return True


def get_input_dir(project_name) -> str or None:
    current_dir = os.path.dirname( os.path.realpath( __file__ ) )
    index = str.find( current_dir, APP )
    return normalize_dir( f'{current_dir[:index]}{APP}/{APP}_UT/{project_name}' ) if index > 0 else None


class XRefTestCase(unittest.TestCase):

    # -----------------------------------------------------------------------------------------------------------------
    #   T e s t s
    # -----------------------------------------------------------------------------------------------------------------

    def test_TC00_SetUp_Db(self):
        global DB
        self.assertTrue( initialize_test(), msg=NOT_CONSISTENT )
        for t in model.DB_tables:
            self.assertTrue( session.db.file_exists( t ) )


# -----------------------------------------------------------------------------------------------------------------
#   M a i n
# -----------------------------------------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
