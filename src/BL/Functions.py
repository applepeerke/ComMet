
from src.DL.Model import KEY_DELIMITER
from src.GL.GeneralException import GeneralException
from src.GL.Validate import format_os

slash = format_os( '/' )


def get_names_from_key(key, no_delimiters) -> list:
    names = key.split( KEY_DELIMITER )
    if len(names) != no_delimiters + 1:
        raise GeneralException(f'{__name__}: key "{key}" does not contain {no_delimiters} delimiters.')
    return names


def format_namespace(namespace) -> str:
    if not namespace:
        return slash
    if not namespace.endswith( slash ):
        return f'{namespace}{slash}'


def split_namespace_and_name(location) -> (str, str):
    names = location.split( '.' )
    name = names[-1] if len( names ) > 1 else names[0]
    namespace = format_namespace( slash.join( names[:-1] ) )
    return name, namespace
