from vuka.core.timestamp import Timestamp


class Container:
    def __init__(self, image=None, **kwargs):
        self.file_name = kwargs.get("file_name")  # None  # Input
        self.frame_index = kwargs.get("frame_index")  # Input
        self.camera_id = kwargs.get("camera_id")  # Input
        self.camera_name = kwargs.get("camera_name")  # Input
        self.width = kwargs.get("width")  # Input
        self.height = kwargs.get("height")  # Input
        self.editable_config = kwargs.get("editable_config")  # Input
        self.image = image  # Input
        self.image_draw = kwargs.get("image_draw")  # Input/Output
        self.image_draw_zone = kwargs.get("image_draw_zone")  # Input/Output
        self.timestamp = Timestamp().timestamp.isoformat()
        self.extra = {}  # для нечетких связей

        if kwargs.get("filtration_parameters_by_size") is not None:
            self.filtration_parameters_by_size = kwargs.get("filtration_parameters_by_size")
        else:
            self.filtration_parameters_by_size = []

        if kwargs.get("objects") is not None:
            self.objects = kwargs.get("objects")
        else:
            self.objects = []  # Output

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        vars(self).update(state)

    # # Только для неопределенных атрибутов
    # def __getattr__(self, attr) -> None:
    #     print(f"attribute {attr} not defined!")
    #     return None

    def __repr__(self):
        repr_str = self.__class__.__name__
        repr_str += (
            "(filename={}, frame_index={}, camera_id={}, width={}, height={}, editable_config={}, "
            "image={}, image_draw={}, image_draw_zone={}, objects={})"
        ).format(
            self.file_name,
            self.frame_index,
            self.camera_id,
            self.width,
            self.height,
            self.editable_config,
            self.image,
            self.image_draw,
            self.image_draw_zone,
            self.objects,
        )
        return repr_str

    def add_obj(self, obj):
        obj.camera_id = self.camera_id
        self.objects.append(obj)
