from src.DL.Model import FD, Model
from src.GL.BusinessLayer.SessionManager import Singleton as Session
from src.GL.Const import APP_NAME
from src.GL.GeneralException import GeneralException
from src.DL.DBDriver.Att import Att
from src.DL.DBDriver.Const import FFD, EMPTY
from src.DL.DBDriver.DBDriver import DBDriver as DB_Driver

model = Model()
session = Session()


class DBInitialize( object ):

    @property
    def messages(self):
        return self._messages

    @property
    def completion_message(self):
        return self._completion_message

    @property
    def solution(self):
        return self._solution

    def __init__(self):

        self._messages = []
        self._completion_message = None
        self._solution = None
        self._error_tables = set()

    def is_consistent(self, force: bool = False) -> bool:
        self._solution = None
        self._error_tables = set()

        if session.unit_test:
            force = True

        if not self._is_valid_model():
            self._solution = 'Review the Model'
            return False

        if not self.connect():
            self._solution = 'Check why the driver can not connect to the database'
            return False

        # A. Check physical tables
        # Error: Optionally rebuild DB and retry.
        self._check_physical_tables()
        if self._error_tables \
                and (force or len( self._error_tables ) == len( model.DB_tables )) \
                and self.rebuild():
            self._check_physical_tables()

        if self._error_tables:
            plur = 's' if len( self._error_tables ) > 1 else EMPTY
            self._solution = f'Rebuild the database (or migrate the table).{plur}'
            return False

        # B. Check model
        # Error: Optionally rebuild DB and retry
        self._check_model()
        if self._error_tables and force and self.rebuild():
            self._check_model()

        if self._error_tables:
            plur = 's' if len( self._error_tables ) > 1 else EMPTY
            verb = 'are' if len( self._error_tables ) > 1 else 'is'
            self._completion_message = f'Table{plur} {verb} inconsistent with the model: ' \
                                       f'\n{", ".join( self._error_tables )}'
            self._solution = f'Rebuild the database or migrate the table{plur}'
            return False

        self._messages.append( 'DBDriver is consistent.' )
        return True

    def _att_exists(self, table_name, att_name, atts, message):
        if att_name not in atts:
            self._error_tables.add( table_name )
            self._messages.append( message )

    def _check_physical_tables(self):
        self._error_tables = {
            table_name for table_name in model.DB_tables
            if not session.db.get_table_description( table_name, check_only=True )}
        self._messages = [ f'Table {t} does not exist in the database.' for t in self._error_tables]

    def _check_model(self):
        self._error_tables = set()

        # Check if FFD in db corresponds with model definition
        for table_name in model.DB_tables:
            ffd_atts = session.db.select( FFD, name=FD.FF_AttName, where=[
                Att( FD.FF_TableName, value=table_name )] )
            att_names = model.get_att_names( table_name, strict=True )
            # Check if all model attributes are present in the FFD
            [self._att_exists(
                table_name, att_name, ffd_atts,
                f'Table {table_name} attribute {att_name} does not exist in the table FFD.' )
                for att_name in att_names]

            # Check if all FFD attributes are present in the model (deleted attribute)
            [self._att_exists(
                table_name, att_name, att_names,
                f'FFD attribute "{att_name}" does not exist in table {table_name}.' )
                for att_name in ffd_atts]

            # Check if all FFD attributes are present in physical file
            schema = session.db.get_table_description( table_name, check_only=True )
            if len( schema ) - 7 != len( ffd_atts ):  # Minus "Id" and "audit data"
                self._messages.append(
                    f'Physical table length minus Id and Audit ({len( schema ) - 7}) '
                    f'is not equal to FFD definition ({len( ffd_atts )}).' )

            schema_atts = [n[0] for n in schema]
            # Check if all FFD attributes are present in physical file
            [self._att_exists(
                table_name, att_name, schema_atts,
                f'FFD attribute "{att_name}" does not exist in the physical table {table_name}.' )
                for att_name in ffd_atts]

            # Check if all physical file attributes are present in FFD
            [self._att_exists(
                table_name, schema_name, ffd_atts,
                f'Schema attribute "{schema_name}" does not exist in FFD table {table_name}.'  )
                for schema_name in schema_atts[1:-6]]

    def rebuild(self) -> bool:
        self._messages = []
        try:
            # Build the tables
            self._db_build()

            # Populate some tables
            self._db_import()
        except GeneralException as ge:
            self._messages.append( ge.message )
            return False
        return True

    @staticmethod
    def connect(db_name: str = APP_NAME) -> bool:
        # Configuration
        if not session:
            raise GeneralException( f'{__name__}: without a session DB can not be connected.' )

        session.db_name = f'{db_name}.db'
        db_dir = session.database_dir

        if not db_dir:
            raise GeneralException( f'{__name__}: DB driver could not be created. Session has no DB directory.' )

        # driver
        db = DB_Driver( f'{db_dir}{session.db_name}' )
        if not db:
            raise GeneralException( f'{__name__}: DB driver could not be created.' )

        # session
        session.db = db
        return True

    @staticmethod
    def _is_valid_model():
        if not model:
            raise GeneralException( f'{__name__}: Model object does not exist.' )
        if not model.is_valid():
            raise GeneralException( model.error_message )
        return True

    @staticmethod
    def _db_build():
        # Build
        for table_name in model.DB_tables:
            session.db.drop_table( table_name )
            session.db.create_table( table_name, model.get_model(table_name) )

    @staticmethod
    def _db_import():
        pass
