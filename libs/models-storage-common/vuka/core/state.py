import logging
import time

from . import BaseObject


class SingletonMetaClass(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingletonMetaClass, cls).__call__(*args, **kwargs)
        return cls._instance


class State(BaseObject, metaclass=SingletonMetaClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # максимальноле кол-во объектов в памяти.
        # при переполнении инициируется удаление старых
        self.max_count_objects = 100

        for k, v in kwargs.items():
            setattr(self, k, v)

    def pop(self):
        it = len(self.objects) - self.max_count_objects

        if it > 0:
            del self.objects[:it]

    def total(self):
        total = 0
        for idx_obj, obj in enumerate(self.objects):
            for idx_sub_obj, sub_obj in enumerate(obj.objects):
                total += 1
        return total

    def remove_old_subobj(self, time_thr):
        t = time.time()
        for idx_obj, obj in enumerate(self.objects):
            print(obj.uuid, len(obj.objects))
            deleted_indices = []
            for idx_sub_obj, sub_obj in enumerate(obj.objects):
                if t - sub_obj.current_timestamp >= time_thr:
                    deleted_indices.append(idx_sub_obj)
            obj.objects = [
                sub_obj for idx_sub_obj, sub_obj in enumerate(obj.objects) if idx_sub_obj not in deleted_indices
            ]
        logging.debug("state included objects: {}".format(self.total()))

    def remove_subobj_by_uuid(self, uuid4):
        for idx_obj, obj in enumerate(self.objects):
            deleted_indices = []
            for idx_sub_obj, sub_obj in enumerate(obj.objects):
                if sub_obj.uuid == uuid4:
                    deleted_indices.append(idx_sub_obj)
            obj.objects = [
                sub_obj for idx_sub_obj, sub_obj in enumerate(obj.objects) if idx_sub_obj not in deleted_indices
            ]

    # def get_detection_index_by_uuid(self, uuid4):
    #     for idx, obj in enumerate(self.objects):
    #         if is_detection(obj):
    #             if obj.uuid == uuid4:
    #                 return idx
    #     return None

    def get_obj_with_image_name(self, camera_id):
        result = []

        for idx, obj in enumerate(self.objects):
            if obj.camera_id == camera_id:
                result.append([idx, obj])
        return result
