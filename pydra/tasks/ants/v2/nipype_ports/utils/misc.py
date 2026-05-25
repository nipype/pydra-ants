import logging

logger = logging.getLogger(__name__)


def is_container(item):
    """Checks if item is a container (list, tuple, dict, set)

    Parameters
    ----------
    item : object
        object to check for .__iter__

    Returns
    -------
    output : Boolean
        True if container
        False if not (eg string)
    """
    return not isinstance(item, str) and hasattr(item, "__iter__")
