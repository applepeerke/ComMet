from src.DL.Enums import Mnemonics as M


class Table(object):
    Containers = 'Containers'
    Modules = 'Modules'
    Classes = 'Classes'
    Functions = 'Functions'
    Repositories = 'Repositories'
    Summary = 'Summary'

    table_code = {
        M.CO: Containers,
        M.MO: Modules,
        M.CL: Classes,
        M.FU: Functions,
        M.RP: Repositories,
        M.SU: Summary,
    }
