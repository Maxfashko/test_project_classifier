class ConfigState(object):
    """contains parameter properties for interacting with non-unified objects"""

    _instance = None

    @classmethod
    def singleton(cls):
        if cls._instance is None:
            cls._instance = ConfigState()
        return cls._instance

    def __init__(self):
        super(ConfigState, self).__init__()
        self.device_id = None
        self.time_exec = []
