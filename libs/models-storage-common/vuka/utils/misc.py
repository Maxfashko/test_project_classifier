from typing import Any, List, Union

from vuka.core import BaseObject


def is_vuka_object(obj: Any) -> bool:
    """Test of obj for belonging to BaseObject.

    Args:
        obj: Any

    Returns:
        True, if the obj is an object of class BaseObject, else False
    """
    if isinstance(obj, BaseObject):
        return True
    return False


def get_object_by_uuid(objects: List, uuid4: str) -> Union[Any]:
    """

    Args:
        objects: vuka.core module class objects.
        uuid4: Universally unique identifier.

    Returns:
        vuka.core module class object.

    """
    for obj in objects:
        if obj.uuid == uuid4:
            return obj
    return None
