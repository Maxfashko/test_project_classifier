# from dataclasses import dataclass
import datetime

# @dataclass
# class Timestamp:
#     """класс реализует метку времени по UTC"""
#
#     timestamp: datetime = datetime.datetime.utcnow()
#
#     def to_sec(self) -> float:
#         return (self.timestamp - datetime.datetime(1970, 1, 1)).total_seconds()


class Timestamp:
    """класс реализует метку времени по UTC"""

    def __init__(self):
        self.timestamp = datetime.datetime.utcnow()

    def to_sec(self) -> float:
        return (self.timestamp - datetime.datetime(1970, 1, 1)).total_seconds()

    def __sub__(self, other):
        if isinstance(other, Timestamp):
            return self.timestamp - other.timestamp
