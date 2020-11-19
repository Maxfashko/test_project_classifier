class OutputData:
    def __init__(self, **kwargs):
        self.width = kwargs.get("width")
        self.height = kwargs.get("height")
        self.fps = kwargs.get("fps")
        self.type = str(kwargs.get("type"))
        self.dir = str(kwargs.get("dir"))
        self.file_name = str(kwargs.get("file_name"))
        if kwargs.get("camera_id") is None:
            self.camera_id = str(0)
        else:
            self.camera_id = kwargs.get("camera_id")

        self.data = []
        self.raw_data = []
        self.vuka_state = []
        self.ms_state = []

    def extend_vuka_state(self, val) -> None:
        self.vuka_state.append(val)

    def extend_ms_state(self, val) -> None:
        self.ms_state.append(val)

    def extend_data(self, val) -> None:
        self.data.append(val)

    def extend_raw_data(self, val) -> None:
        self.raw_data.append(val)

    def to_json(self, dump_raw_data=False, dump_vuka_state=False, dump_ms_state=False):
        return {
            "info": {
                "width": self.width,
                "height": self.height,
                "fps": self.fps,
                "type": self.type,
                "dir": self.dir,
                "file_name": self.file_name,
                "camera_id": self.camera_id,
            },
            "data": self.data,
            "raw_data": self.raw_data if dump_raw_data else [],  # для десериализации
            "vuka_state": self.vuka_state if dump_vuka_state else [],  # внутреннее состояние vuka объектов
            "ms_state": self.ms_state if dump_ms_state else [],  # внутреннее состояние models-storage объектов
        }
