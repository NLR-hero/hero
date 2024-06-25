

class ServiceBase:
    def __init__(self, clientInstance):
        self.client = clientInstance
        self._configure()
        self._after_init()

    def _configure(self):
        return None

    def _after_init(self):
        return None
