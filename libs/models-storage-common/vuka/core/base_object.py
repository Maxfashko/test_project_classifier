import time
import uuid


class BaseObject:
    def __init__(self):
        self.uuid = str(uuid.uuid4())
        self.objects = []
        self.violator = False
        self.image_name = None
        self.camera_id = None
        self.detection_count = 1
        self.image = None
        self.image_draw = None
        self.current_timestamp = time.time()
        self.zones = set()
        self._type = "base_object"

    def serialization_to_json(self):
        return dict(self.__dict__)

    @property
    def type(self):
        return self._type
