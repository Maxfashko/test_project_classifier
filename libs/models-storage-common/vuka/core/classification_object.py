import logging
from typing import Any, List

from vuka.core import BaseObject
from vuka.utils import is_vuka_object


class ClassificationObject(BaseObject):
    """Provides an interface for working with objects in the tasks of classification objects.

        Args:
            score: Classifier score.
            label: Classifier label.
    """

    def __init__(self, score: float, label: str) -> None:
        super(ClassificationObject, self).__init__()
        self.score: float = score
        self.label: str = label
        self._type: str = "classification"

    @property
    def score(self) -> float:
        return self.__score

    @score.setter
    def score(self, score) -> None:
        if not isinstance(score, float):
            raise TypeError("score must be float object")
        self.__score = score

    @property
    def label(self) -> str:
        return self.__label

    @label.setter
    def label(self, label) -> None:
        if not isinstance(label, str):
            raise TypeError("label must be string object")
        self.__label = label


def is_classification(obj: Any) -> bool:
    """Checks if an obj is an object of class ClassificationObject.

    Args:
        obj: vuka.core module class objects.

    Returns:
        True, if the obj is an object of class ClassificationObject, else False
    """
    if not is_vuka_object(obj):
        # raise TypeError("obj must be the heir of BaseObject")
        logging.error("obj must be the heir of BaseObject")
        return False

    return True if obj.type == "classification" else False


def get_classification_objects(objects: List) -> List:
    """Returns a list of instances of objects of the class ClassificationObject.

    Args:
        objects: List of vuka.core module class objects.

    Returns:
        List of instances of objects of the class ClassificationObject.
    """
    return [obj for obj in objects if is_classification(obj)]
