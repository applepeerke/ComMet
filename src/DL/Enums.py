from src.GL.DataLayer.MessageDef import MessageDef
from src.GL.Enums import MessageSeverity


class ContainerType( object ):
    Module = 'Module'
    Class = 'Class'
    Function = 'Function'
    Unknown = '*Unknown'


class FunctionType( object ):
    Property = 'Property'
    Function = 'Function'
    Method = 'Method'
    Internal = '*Internal'


class Mnemonics( object ):
    CP = 'CP'
    MO = 'MO'
    CL = 'CL'
    FU = 'FU'
    CO = 'CO'
    RP = 'RP'
    SU = 'SU'


class MessageCodes( object ):
    MSG_IMPORT_NOT_FOUND = MessageDef('Import not found', MessageSeverity.Info )
    MSG_IMPORT_NOT_FOUND_FROM_SPECIFIED_NAMESPACE = MessageDef(
        'Import not found from namespace', MessageSeverity.Warning )
    MSG_UNKNOWN_TYPE = MessageDef('Unknown type', MessageSeverity.Error )
