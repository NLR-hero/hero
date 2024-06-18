from ...config import get_task_engine_api
from ...api import ApiBase

class TaskEngineApi(ApiBase):
    def __init__(self, resilient_session=False):
        super().__init__(resilient_session)
        self.base_url = get_task_engine_api()