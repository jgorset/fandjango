from settings import DISABLED_PATHS
from settings import ENABLED_PATHS

def is_disabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the DISABLED_PATHS setting.

    Arguments:
    path -- A string describing the path to be matched.
    """
    for disabled_path in DISABLED_PATHS:
        match = re.search(disabled_path, path[1:])
        if match:
            return True
    return False

def is_enabled_path(path):
    """
    Determine whether or not the path matches one or more paths
    in the ENABLED_PATHS setting.

    Arguments:
    path -- A string describing the path to be matched.
    """
    for enabled_path in ENABLED_PATHS:
        match = re.search(enabled_path, path[1:])
        if match:
            return True
    return False
