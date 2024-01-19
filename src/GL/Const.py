APP = 'App'
APP_NAME = 'ComMet'
DB = APP_NAME
FFD = 'FFD'
ALL = 'All'
ANY = 'Any'
NONE = 'None'
BASE_OUTPUT_SUBDIR = f'{APP_NAME.lower()}_result'
EMPTY = ''
BLANK = ' '
ZERO = '0'
NC = 'NO_CHG'
N = 'n'
NO = 'No'
Y = 'y'
YES = 'Yes'
UNKNOWN = 'Unknown'
NOT_FOUND = 'Not found'
NOT_A_CLASS = '*NOT_A_CLASS'
FALSE = 'False'
TRUE = 'True'
DONE = 'Done.'
OK = 'OK'
ER = 'ER'
ASTERISK = '*'

RESULTS_DIR = 'Results'
CSV_EXT = '.csv'

APOSTROPHES = ( '\'', '"', "\\'" )

LC = 'abcdefghijklmnopqrstuvwxyz'
UC = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
NUM = '0123456789'
SPECIAL_ALLOWED_CHARS = '_'
CODE_LC = f'{LC}{NUM}{SPECIAL_ALLOWED_CHARS}'

# Errors
INFO = 'Info'
ERROR = 'Error'
EXCEPTION = 'Exception'
WARNING = 'Warning'

MAX_READS_PER_FILE = 100000
MAX_WRITES_PER_FILE = 100000
MAX_VALIDATION_ERRORS = 100
MAX_LOOP_COUNT = 10000
MAX_PATTERN_LENGTH_AT_QUICK_SCAN = 50
MAX_CONFIG_FILE_SIZE_IN_BYTES = 1000000
CSV_FIELD_LIMIT = 131000
XLS_FIELD_LIMIT = 32000
APP_FIELD_LIMIT = 1000